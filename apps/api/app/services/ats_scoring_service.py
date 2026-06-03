import re
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import ATSScore, Candidate, CandidateMatch, JobDescription, Resume
from app.schemas.ats import ATSScoreComponent, ATSScoreRead
from app.schemas.matching import CandidateMatchRead, MatchingWeights
from app.services.matching_service import CandidateEvidence, MatchingService


class ATSScoringService:
    sections = ["experience", "education", "skills", "projects"]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def score_candidate_for_job(
        self,
        job: JobDescription,
        candidate: Candidate,
        resume: Resume,
        semantic_score: float = 0.0,
        skills: list[str] | None = None,
    ) -> ATSScoreRead:
        skills = skills or []
        match = MatchingService(self.db).score(
            job,
            CandidateEvidence(candidate=candidate, resume=resume, skills=skills, semantic_score=semantic_score),
            MatchingWeights(),
            {},
        )
        text = resume.extracted_text or ""
        lower = text.lower()
        issues: list[str] = []
        recommendations: list[str] = []

        present_sections = [section for section in self.sections if section in lower]
        section_score = len(present_sections) / len(self.sections) * 30
        tokens = set(re.findall(r"[A-Za-z][A-Za-z0-9\+#\.-]{2,}", text))
        keyword_score = min(25, len(tokens) / 12)
        word_count = len(text.split())
        readability_score = 20 if 250 <= word_count <= 2500 else 10
        has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+", text))
        contact_score = 15 if has_email else 5
        formatting_clean = "\t" not in text and len(re.findall(r"[^\x00-\x7F]", text)) < 20
        formatting_score = 10 if formatting_clean else 6

        for section in self.sections:
            if section not in lower:
                issues.append(f"Missing or unclear {section} section")
                recommendations.append(f"Add a clearly labeled {section.title()} section")
        if contact_score < 15:
            issues.append("No email address detected")
            recommendations.append("Include a professional email address near the top")
        if readability_score < 20:
            issues.append("Resume length may hurt readability")
            recommendations.append("Keep resume content concise and role-focused")

        resume_quality_score = round(section_score + keyword_score + readability_score + contact_score + formatting_score, 2)
        score = round((match.overall_score * 0.82) + (resume_quality_score * 0.18), 2)
        components = [
            ATSScoreComponent(
                name="semantic_similarity",
                score=match.semantic_score,
                weight=40,
                evidence=[f"Candidate resume embedding compared against {job.title}"],
            ),
            ATSScoreComponent(
                name="skill_weighting",
                score=match.skill_match,
                weight=25,
                evidence=[f"Matched skills: {', '.join(match.matched_skills[:8]) or 'none'}"],
            ),
            ATSScoreComponent(
                name="experience_fit",
                score=match.experience_match,
                weight=15,
                evidence=[f"Required minimum: {job.years_experience_min or 'not specified'} years"],
            ),
            ATSScoreComponent(
                name="education_fit",
                score=match.education_match,
                weight=10,
                evidence=job.education_requirements or ["No explicit education requirement"],
            ),
            ATSScoreComponent(
                name="keyword_match",
                score=match.keyword_score,
                weight=10,
                evidence=[f"Keyword overlap calculated from {len(job.keywords or [])} JD terms"],
            ),
            ATSScoreComponent(
                name="resume_section_coverage",
                score=round(section_score, 2),
                weight=6,
                evidence=[f"{section} section detected" for section in present_sections],
            ),
            ATSScoreComponent(
                name="resume_keyword_density",
                score=round(keyword_score, 2),
                weight=5,
                evidence=[f"{len(tokens)} unique resume terms detected"],
            ),
            ATSScoreComponent(
                name="resume_readability",
                score=readability_score,
                weight=4,
                evidence=[f"{word_count} words extracted"],
            ),
            ATSScoreComponent(
                name="resume_contactability",
                score=contact_score,
                weight=2,
                evidence=["email detected" if has_email else "email not detected"],
            ),
            ATSScoreComponent(
                name="resume_formatting_parseability",
                score=formatting_score,
                weight=1,
                evidence=["clean parser-friendly text" if formatting_clean else "formatting noise detected"],
            ),
        ]
        for missing_skill in match.missing_skills[:6]:
            issues.append(f"Missing job skill: {missing_skill}")
            recommendations.append(f"Validate or develop evidence for {missing_skill}")
        explanation = self._explain(score, components, issues, job)
        await self._persist_match(job.organization_id, job.owner_id, job.id, match)
        await self.db.execute(
            delete(ATSScore).where(
                ATSScore.organization_id == resume.organization_id,
                ATSScore.candidate_id == candidate.id,
                ATSScore.job_description_id == job.id,
            )
        )
        record = ATSScore(
            organization_id=resume.organization_id,
            owner_id=resume.owner_id,
            candidate_id=candidate.id,
            job_description_id=job.id,
            resume_id=resume.id,
            ats_score=score,
            components=[component.model_dump() for component in components],
            issues=issues,
            recommendations=recommendations,
            explanation=explanation,
            scoring_version="ats-job-context-v1",
        )
        self.db.add(record)
        await self.db.commit()
        return ATSScoreRead(
            candidate_id=candidate.id,
            job_description_id=job.id,
            resume_id=resume.id,
            ats_score=score,
            components=components,
            issues=issues,
            recommendations=recommendations,
            explanation=explanation,
        )

    @staticmethod
    def _explain(score: float, components: list[ATSScoreComponent], issues: list[str], job: JobDescription) -> str:
        strongest = max(components, key=lambda item: item.score / max(item.weight, 1))
        weakest = min(components, key=lambda item: item.score / max(item.weight, 1))
        if score >= 80:
            verdict = f"Candidate is a strong ATS fit for {job.title}."
        elif score >= 60:
            verdict = f"Candidate is a partial ATS fit for {job.title}; review gaps before shortlisting."
        else:
            verdict = f"Candidate is currently a weak ATS fit for {job.title}."
        issue_text = f" Primary issue: {issues[0]}." if issues else ""
        return f"{verdict} Strongest signal: {strongest.name}. Weakest signal: {weakest.name}.{issue_text}"

    async def _persist_match(self, organization_id: UUID, owner_id: UUID, job_id: UUID, match: CandidateMatchRead) -> None:
        await self.db.execute(
            delete(CandidateMatch).where(
                CandidateMatch.organization_id == organization_id,
                CandidateMatch.candidate_id == match.candidate_id,
                CandidateMatch.job_description_id == job_id,
            )
        )
        self.db.add(
            CandidateMatch(
                organization_id=organization_id,
                owner_id=owner_id,
                candidate_id=match.candidate_id,
                job_description_id=job_id,
                overall_score=match.overall_score,
                semantic_score=match.semantic_score,
                skill_match=match.skill_match,
                experience_match=match.experience_match,
                education_match=match.education_match,
                keyword_score=match.keyword_score,
                matched_skills=match.matched_skills,
                missing_skills=match.missing_skills,
                explanation=match.explanation,
                scoring_version="ats-job-context-v1",
            )
        )
