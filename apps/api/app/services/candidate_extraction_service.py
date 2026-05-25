from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
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
                    "full_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "skills": {"type": "array", "items": {"type": "string"}},
                    "education": {"type": "array", "items": {"type": "string"}},
                    "experience": {"type": "array", "items": {"type": "string"}},
                    "projects": {"type": "array", "items": {"type": "string"}},
                    "inferred_seniority": {"type": "string"},
                    "summary": {"type": "string"},
                },
            }
            result = await provider.complete_structured(
                prompt=f"Extract recruiting intelligence from this resume text. Return only factual evidence.\n\n{text[:12000]}",
                schema=schema,
                system="You are a recruiting intelligence extractor. Use null or empty arrays when evidence is absent.",
                options=GenerationOptions(temperature=0.0, max_output_tokens=1200),
                feature="resume_structured_extraction",
            )
            data = result.structured_data or json.loads(result.text)
            return CandidateExtraction(
                full_name=str(data.get("full_name") or "Candidate Profile").strip(),
                email=data.get("email") or None,
                phone=data.get("phone") or None,
                skills=self._clean_list(data.get("skills")),
                education=self._clean_list(data.get("education")),
                experience=self._clean_list(data.get("experience")),
                projects=self._clean_list(data.get("projects")),
                inferred_seniority=data.get("inferred_seniority") or None,
                summary=data.get("summary") or None,
                source="gemini",
                raw={"gemini_model": getattr(result, "model", None)},
            )
        except Exception:
            return None

    def _deterministic_extract(self, text: str, filename: str | None, metadata: dict) -> CandidateExtraction:
        identity = CandidateIdentityExtractor().extract(text, filename, metadata)
        full_name = identity.full_name
        if full_name == "Candidate Profile":
            full_name = self._last_resort_name(identity.email, filename)
        lower = text.lower()
        skills = sorted({skill for skill in SKILL_TERMS if skill in lower})
        sections = {name: self._section_lines(text, aliases) for name, aliases in SECTION_HEADERS.items()}
        years = [int(value) for value in re.findall(r"(\d+)\+?\s*(?:years|yrs)", lower)]
        seniority = self._seniority(max(years) if years else None, lower)
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
        if gemini.full_name == "Candidate Profile":
            gemini.full_name = fallback.full_name
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

    @staticmethod
    def _seniority(years: int | None, text: str) -> str | None:
        if years is not None:
            if years >= 8:
                return "senior"
            if years >= 3:
                return "mid"
            return "junior"
        if any(term in text for term in ["lead", "principal", "staff engineer", "architect"]):
            return "senior"
        if any(term in text for term in ["intern", "trainee", "entry level"]):
            return "junior"
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
        return "Imported Candidate"
