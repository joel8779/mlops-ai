from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings
from app.services.candidate_identity import CandidateIdentityExtractor
from app.services.job_intelligence_service import SKILL_TERMS


SECTION_HEADERS = {
    "education": ["education", "academic"],
    "experience": ["experience", "employment", "work history", "professional experience"],
    "projects": ["projects", "portfolio"],
    "skills": ["skills", "technical skills", "technologies"],
}

CANDIDATE_SKILL_TERMS = SKILL_TERMS | {
    "html",
    "css",
    "tailwind",
    "bootstrap",
    "sql",
    "nosql",
    "git",
    "github",
    "gitlab",
    "jira",
    "figma",
    "excel",
    "power bi",
    "tableau",
    "c",
    "c++",
    "c#",
    "php",
    "laravel",
    "ruby",
    "rails",
    "swift",
    "kotlin",
    "android",
    "ios",
    "vue",
    "angular",
    "redux",
    "express",
    "nestjs",
    "prisma",
    "supabase",
    "firebase",
    "sqlite",
    "oracle",
    "communication",
    "leadership",
}

SKILL_ALIASES = {
    "reactjs": "react",
    "react.js": "react",
    "nextjs": "next.js",
    "nodejs": "node.js",
    "node": "node.js",
    "postgres": "postgresql",
    "postgre sql": "postgresql",
    "k8s": "kubernetes",
    "tf": "tensorflow",
    "sklearn": "scikit-learn",
    "hugging face": "huggingface",
    "ms excel": "excel",
    "powerbi": "power bi",
}


@dataclass
class CandidateExtraction:
    full_name: str
    email: str | None
    phone: str | None
    skills: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    inferred_seniority: str | None = None
    summary: str | None = None
    source: str = "deterministic"
    warnings: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


class CandidateExtractionService:
    async def extract(
        self,
        text: str,
        filename: str | None,
        metadata: dict | None = None,
        use_gemini: bool = True,
    ) -> CandidateExtraction:
        metadata = metadata or {}
        gemini = await self._gemini_extract(text) if use_gemini else None
        deterministic = self._deterministic_extract(text, filename, metadata)
        if gemini:
            return self._merge(gemini, deterministic)
        return deterministic

    async def _gemini_extract(self, text: str) -> CandidateExtraction | None:
        if not settings.gemini_api_key:
            return None
        try:
            from app.services.llm_provider import get_llm_provider
            from app.services.llm.providers.gemini_provider import GenerationOptions

            provider = get_llm_provider()
            if not hasattr(provider, "complete_structured"):
                return None
            schema = {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "skills": {"type": "array", "items": {"type": "string"}},
                    "education": {"type": "array", "items": {"type": "string"}},
                    "experience": {"type": "array", "items": {"type": "string"}},
                    "projects": {"type": "array", "items": {"type": "string"}},
                    "summary": {"type": "string"},
                },
            }
            result = await provider.complete_structured(
                prompt=f"Extract recruiting intelligence from this resume text. Do not infer or return candidate identity. Return only factual evidence.\n\n{text[:12000]}",
                schema=schema,
                system="You extract recruiting intelligence only. Do not determine candidate names. Use null or empty arrays when evidence is absent.",
                options=GenerationOptions(temperature=0.0, max_output_tokens=1200),
                feature="resume_structured_extraction",
            )
            data = result.structured_data or json.loads(result.text)
            return CandidateExtraction(
                full_name="Uploaded Candidate",
                email=data.get("email") or None,
                phone=data.get("phone") or None,
                skills=self._filter_evidenced_skills(self._clean_list(data.get("skills")), text),
                education=self._clean_list(data.get("education")),
                experience=self._clean_list(data.get("experience")),
                projects=self._clean_list(data.get("projects")),
                inferred_seniority=None,  # Never infer from Gemini - use structured fields only
                summary=data.get("summary") or None,
                source="gemini",
                raw={"gemini_model": getattr(result, "model", None)},
            )
        except Exception:
            return None

    def _deterministic_extract(self, text: str, filename: str | None, metadata: dict) -> CandidateExtraction:
        identity = CandidateIdentityExtractor().extract(text, filename, metadata)
        full_name = identity.full_name
        if full_name in {"Candidate Profile", "Uploaded Candidate"}:
            full_name = self._last_resort_name(identity.email, filename)
        lower = text.lower()
        skills = self.extract_skills(text)
        sections = {name: self._section_lines(text, aliases) for name, aliases in SECTION_HEADERS.items()}
        years = self._experience_years(lower)
        seniority = self._experience_level(max(years) if years else None, lower, sections["experience"], sections["education"])
        summary = self._summary(text, skills, seniority)
        return CandidateExtraction(
            full_name=full_name,
            email=identity.email,
            phone=identity.phone,
            skills=skills,
            education=sections["education"],
            experience=sections["experience"],
            projects=sections["projects"],
            inferred_seniority=seniority,
            summary=summary,
            source=identity.source,
            raw={"identity_source": identity.source, "detected_years": years},
        )

    def _merge(self, gemini: CandidateExtraction, fallback: CandidateExtraction) -> CandidateExtraction:
        gemini.email = gemini.email or fallback.email
        gemini.phone = gemini.phone or fallback.phone
        gemini.skills = sorted(set(gemini.skills) | set(fallback.skills))
        gemini.education = gemini.education or fallback.education
        gemini.experience = gemini.experience or fallback.experience
        gemini.projects = gemini.projects or fallback.projects
        gemini.inferred_seniority = gemini.inferred_seniority or fallback.inferred_seniority
        gemini.summary = gemini.summary or fallback.summary
        gemini.raw = {**fallback.raw, **gemini.raw, "fallback_source": fallback.source}
        return gemini

    @staticmethod
    def _section_lines(text: str, aliases: list[str]) -> list[str]:
        lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
        captured: list[str] = []
        active = False
        for line in lines:
            lower = line.lower().strip(":")
            if any(lower == alias or lower.startswith(f"{alias}:") for alias in aliases):
                active = True
                continue
            if active and any(lower == alias for names in SECTION_HEADERS.values() for alias in names):
                break
            if active and len(line) > 4:
                captured.append(line[:240])
            if len(captured) >= 8:
                break
        return captured

    @classmethod
    def extract_skills(cls, text: str) -> list[str]:
        lower = text.lower()
        found = {skill for skill in CANDIDATE_SKILL_TERMS if cls._term_present(lower, skill)}
        for alias, canonical in SKILL_ALIASES.items():
            if cls._term_present(lower, alias):
                found.add(canonical)
        for item in cls._skills_section_candidates(text):
            normalized = cls.normalize_skill(item)
            if normalized and cls._term_present(lower, item.lower()):
                found.add(normalized)
        return sorted(found)

    @classmethod
    def normalize_skills(cls, skills: list[str] | None, evidence_text: str | None = None) -> list[str]:
        evidence = evidence_text.lower() if evidence_text else None
        normalized: set[str] = set()
        for skill in skills or []:
            value = cls.normalize_skill(skill)
            if not value:
                continue
            if evidence is not None and not cls._term_present(evidence, skill.lower()) and not cls._term_present(evidence, value):
                continue
            normalized.add(value)
        return sorted(normalized)

    @staticmethod
    def normalize_skill(skill: str) -> str | None:
        value = str(skill).strip()
        # Strip leading bullet/list markers
        value = re.sub(r"^[*\-•▪◦‣⁃\s]+", "", value)
        value = re.sub(r"\s+", " ", value.strip().lower())
        value = value.strip(".,;:()[]{}")
        if not value or len(value) > 80:
            return None
        return SKILL_ALIASES.get(value, value)

    @classmethod
    def _filter_evidenced_skills(cls, skills: list[str], text: str) -> list[str]:
        explicit = cls.normalize_skills(skills, text)
        deterministic = cls.extract_skills(text)
        return sorted(set(explicit) | set(deterministic))

    @staticmethod
    def _term_present(lower_text: str, lower_term: str) -> bool:
        term = re.escape(lower_term.strip().lower())
        if not term:
            return False
        return re.search(rf"(?<![a-z0-9]){term}(?![a-z0-9])", lower_text) is not None

    @staticmethod
    def _skills_section_candidates(text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        candidates: list[str] = []
        active = False
        for line in lines:
            lower = line.lower().strip(":")
            if any(lower == alias or lower.startswith(f"{alias}:") for alias in SECTION_HEADERS["skills"]):
                active = True
                line = re.sub(r"(?i)^(technical\s+skills|technologies|skills)\s*:?", "", line).strip()
            elif active and any(lower == alias for names in SECTION_HEADERS.values() for alias in names if alias not in SECTION_HEADERS["skills"]):
                break
            if active:
                candidates.extend(part.strip() for part in re.split(r"[,|;/•]", line) if part.strip())
            if len(candidates) >= 40:
                break
        return candidates

    @staticmethod
    def _experience_years(text: str) -> list[int]:
        patterns = [
            r"(\d{1,2})\+?\s*(?:years|yrs)\s+(?:of\s+)?(?:professional\s+|full[-\s]?time\s+)?experience",
            r"(?:experience|worked)\s*(?:of|for)?\s*(\d{1,2})\+?\s*(?:years|yrs)",
        ]
        years: list[int] = []
        for pattern in patterns:
            years.extend(int(value) for value in re.findall(pattern, text))
        return [year for year in years if 0 <= year <= 50]

    @classmethod
    def _experience_level(cls, years: int | None, text: str, experience: list[str], education: list[str]) -> str | None:
        lower = text.lower()
        current_year = datetime.now(timezone.utc).year
        
        # 1. Parse employment timeline to compute years of experience
        exp_text = "\n".join(experience).lower()
        timeline_years = None
        ranges = re.findall(r"\b(20\d{2})\s*[-–]\s*(present|current|20\d{2})\b", exp_text)
        if ranges:
            durations = []
            for start_str, end_str in ranges:
                start = int(start_str)
                end = current_year if end_str in ("present", "current") else int(end_str)
                if end >= start and 1970 <= start <= current_year + 1:
                    durations.append(end - start)
            if durations:
                timeline_years = sum(durations)
        
        # Priority 1: Employment timeline years
        # Priority 2: Explicit years parsed
        effective_years = timeline_years if timeline_years is not None else years
        
        # 3. Check for student / graduation year
        graduation_years = [
            int(value)
            for value in re.findall(r"(?:graduat(?:e|ion|ing)|class of|batch of|b\.?tech|bachelor|master|degree)[^\n]{0,80}\b(20\d{2})\b", text)
        ]
        has_current_or_future_graduation = any(year >= current_year for year in graduation_years)
        no_professional_experience = (effective_years is None or effective_years == 0) and not cls._has_professional_role(text, experience)
        
        is_student = "student" in lower or "studying" in lower or (has_current_or_future_graduation and no_professional_experience)
        
        # 4. Check for internship status
        is_intern = "intern" in lower or "internship" in lower
        
        # Priority 3 & 4: Interns and Students override senior/mid classification if no substantial professional timeline exists
        if is_student:
            return "student"
            
        if is_intern and (effective_years is None or effective_years <= 1):
            return "intern"
            
        # 5. Weak signal: title keywords
        senior_terms = ["senior", "sr.", "lead", "principal", "architect", "manager", "director", "vp", "head"]
        has_senior_title = any(rf"\b{term}\b" in exp_text for term in senior_terms)
        
        if effective_years is None:
            # Check other keywords
            if any(term in lower for term in ["fresher", "fresh graduate", "entry level", "entry-level"]):
                return "fresher"
            return None
            
        if effective_years <= 1:
            return "fresher"
        elif effective_years <= 3:
            return "junior"
        elif effective_years <= 6:
            # Mid-level, but if weak signal (senior title) is present, elevate to senior
            if has_senior_title:
                return "senior"
            return "mid-level"
        else: # effective_years >= 7
            return "senior"

    @staticmethod
    def _has_professional_role(text: str, experience: list[str]) -> bool:
        role_text = "\n".join(experience).lower() or text
        professional_terms = [
            "software engineer",
            "developer",
            "analyst",
            "consultant",
            "manager",
            "specialist",
            "associate",
            "full-time",
            "full time",
        ]
        if any(term in role_text for term in professional_terms):
            return True
        return bool(re.search(r"\b(20\d{2})\s*[-–]\s*(present|current|20\d{2})\b", role_text)) and "intern" not in role_text

    @staticmethod
    def headline(extraction: CandidateExtraction) -> str | None:
        skills = extraction.skills[:3]
        if extraction.inferred_seniority and skills:
            return f"{extraction.inferred_seniority.title()} candidate with {', '.join(skills)}"
        if skills:
            return f"Candidate with {', '.join(skills)}"
        return None

    @staticmethod
    def _summary(text: str, skills: list[str], seniority: str | None) -> str:
        words = " ".join(text.split())[:220]
        skill_text = f" Skills detected: {', '.join(skills[:6])}." if skills else ""
        seniority_text = f" Inferred seniority: {seniority}." if seniority else ""
        return f"{words}{skill_text}{seniority_text}".strip()

    @staticmethod
    def _clean_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return sorted({str(item).strip().lower() for item in value if str(item).strip()})

    @staticmethod
    def _last_resort_name(email: str | None, filename: str | None) -> str:
        source = ""
        if email and "@" in email:
            source = email.split("@", 1)[0]
        elif filename:
            source = re.sub(r"\.[A-Za-z0-9]+$", "", filename)
        source = re.sub(r"(?i)\b(resume|cv|profile|latest|final|updated)\b", " ", source)
        parts = [part for part in re.split(r"[^A-Za-z]+", source) if len(part) > 1 and not part.isdigit()]
        if parts:
            return " ".join(part.capitalize() for part in parts[:4])
        return "Uploaded Candidate"
