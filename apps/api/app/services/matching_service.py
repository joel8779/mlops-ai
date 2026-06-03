from dataclasses import dataclass
from math import exp
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.logging import get_logger
from app.models.domain import Candidate, CandidateMatch, CandidatePipelineStage, JobDescription, PipelineStage, Resume
from app.repositories.candidates import CandidateRepository
from app.schemas.matching import CandidateMatchRead, MatchingWeights
from app.services.embedding_service import EmbeddingService

logger = get_logger(__name__)


@dataclass(frozen=True)
class CandidateEvidence:
    candidate: Candidate
    resume: Resume | None
    skills: list[str]
    semantic_score: float


class MatchingService:
    scoring_version = "hybrid-v1"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.candidates = CandidateRepository(db)

    async def rank_candidates(
        self,
        organization_id: UUID,
        owner_id: UUID,
        job: JobDescription,
        limit: int,
        weights: MatchingWeights | None = None,
        recruiter_preferences: dict | None = None,
    ) -> list[CandidateMatchRead]:
        weights = weights or MatchingWeights(
            semantic=settings.match_semantic_weight,
            skill=settings.match_skill_weight,
            experience=settings.match_experience_weight,
            education=settings.match_education_weight,
            keyword=settings.match_keyword_weight,
        )
        try:
            semantic_hits = EmbeddingService().semantic_search(organization_id, owner_id, job.description, limit=limit * 3)
        except Exception as exc:
            logger.exception(
                "semantic_search_failed",
                organization_id=str(organization_id),
                owner_id=str(owner_id),
                job_id=str(job.id),
                error=str(exc),
            )
            semantic_hits = []
        semantic_by_candidate = {
            UUID(hit["payload"]["candidate_id"]): min(100.0, max(0.0, hit["score"] * 100))
            for hit in semantic_hits
            if hit.get("payload", {}).get("candidate_id")
        }
        candidates = await self.candidates.list_for_org(organization_id, limit=limit * 3)
        scored: list[CandidateMatchRead] = []
        for candidate in candidates:
            resume = await self.candidates.latest_resume(candidate.id, organization_id)
            skills = await self.candidates.skills_for_candidate(candidate.id, organization_id)
            evidence = CandidateEvidence(
                candidate=candidate,
                resume=resume,
                skills=skills,
                semantic_score=semantic_by_candidate.get(candidate.id, 0.0)
                or self._semantic_fallback_score(job, resume, skills),
            )
            scored.append(self.score(job, evidence, weights, recruiter_preferences or {}))
        scored.sort(key=lambda item: item.overall_score, reverse=True)
        await self._persist(organization_id, owner_id, job.id, scored[:limit])
        return scored[:limit]

    def score(
        self,
        job: JobDescription,
        evidence: CandidateEvidence,
        weights: MatchingWeights,
        recruiter_preferences: dict,
    ) -> CandidateMatchRead:
        job_skills = set(job.required_skills + job.optional_skills)
        candidate_skills = set(evidence.skills)
        matched_skills = sorted(job_skills & candidate_skills)
        missing_skills = sorted(set(job.required_skills) - candidate_skills)
        skill_score = 100.0 if not job_skills else len(matched_skills) / len(job_skills) * 100
        experience_score = self._experience_score(job, evidence.resume)
        education_score = self._education_score(job, evidence.resume)
        keyword_score = self._keyword_score(job, evidence.resume)
        preference_bonus = self._preference_bonus(recruiter_preferences, evidence)
        total_weight = weights.semantic + weights.skill + weights.experience + weights.education + weights.keyword
        weighted = (
            evidence.semantic_score * weights.semantic
            + skill_score * weights.skill
            + experience_score * weights.experience
            + education_score * weights.education
            + keyword_score * weights.keyword
        ) / max(total_weight, 0.01)
        overall = min(100.0, weighted + preference_bonus)
        return CandidateMatchRead(
            candidate_id=evidence.candidate.id,
            overall_score=round(overall, 2),
            semantic_score=round(evidence.semantic_score, 2),
            skill_match=round(skill_score, 2),
            experience_match=round(experience_score, 2),
            education_match=round(education_score, 2),
            keyword_score=round(keyword_score, 2),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            explanation=self._explain(job, matched_skills, missing_skills, overall),
        )

    async def _persist(self, organization_id: UUID, owner_id: UUID, job_id: UUID, matches: list[CandidateMatchRead]) -> None:
        await self.db.execute(
            delete(CandidateMatch).where(
                CandidateMatch.organization_id == organization_id,
                CandidateMatch.job_description_id == job_id,
            )
        )
        for position, match in enumerate(matches):
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
                    scoring_version=self.scoring_version,
                )
            )
            current_stage = await self.db.scalar(
                select(CandidatePipelineStage).where(
                    CandidatePipelineStage.organization_id == organization_id,
                    CandidatePipelineStage.candidate_id == match.candidate_id,
                    CandidatePipelineStage.job_description_id == job_id,
                    CandidatePipelineStage.deleted_at.is_(None),
                )
            )
            if current_stage is None:
                self.db.add(
                    CandidatePipelineStage(
                        organization_id=organization_id,
                        owner_id=owner_id,
                        candidate_id=match.candidate_id,
                        job_description_id=job_id,
                        stage=PipelineStage.ranked,
                        position=position,
                        metadata_json={"source": "matching.rank_candidates"},
                    )
                )
            elif current_stage.stage in {PipelineStage.uploaded, PipelineStage.ranked}:
                current_stage.stage = PipelineStage.ranked
                current_stage.position = position
                current_stage.metadata_json = {
                    **(current_stage.metadata_json or {}),
                    "source": "matching.rank_candidates",
                }
        await self.db.commit()

    @staticmethod
    def _experience_score(job: JobDescription, resume: Resume | None) -> float:
        if job.years_experience_min is None:
            return 100.0
        text = (resume.extracted_text if resume else "") or ""
        import re

        years = [int(value) for value in re.findall(r"(\d+)\+?\s*(?:years|yrs)", text.lower())]
        candidate_years = max(years) if years else 0
        return min(100.0, candidate_years / max(job.years_experience_min, 1) * 100)

    @staticmethod
    def _education_score(job: JobDescription, resume: Resume | None) -> float:
        if not job.education_requirements:
            return 100.0
        text = ((resume.extracted_text if resume else "") or "").lower()
        found = [term for term in job.education_requirements if term in text]
        return len(found) / len(job.education_requirements) * 100

    @staticmethod
    def _keyword_score(job: JobDescription, resume: Resume | None) -> float:
        if not job.keywords:
            return 100.0
        text = ((resume.extracted_text if resume else "") or "").lower()
        found = [keyword for keyword in job.keywords[:20] if keyword.lower() in text]
        return len(found) / min(len(job.keywords), 20) * 100

    @staticmethod
    def _preference_bonus(preferences: dict, evidence: CandidateEvidence) -> float:
        location = preferences.get("location")
        if location and evidence.candidate.location and location.lower() in evidence.candidate.location.lower():
            return 3.0
        return 0.0

    @staticmethod
    def _semantic_fallback_score(job: JobDescription, resume: Resume | None, skills: list[str]) -> float:
        if resume is None or not resume.extracted_text:
            return 0.0
        text = resume.extracted_text.lower()
        job_terms = {term.lower() for term in [*(job.required_skills or []), *(job.optional_skills or []), *(job.keywords or [])]}
        skill_hits = {skill.lower() for skill in skills if skill.lower() in job_terms}
        keyword_hits = {term for term in list(job_terms)[:40] if term and term in text}
        if not job_terms:
            return 35.0
        coverage = (len(skill_hits) * 1.5 + len(keyword_hits)) / max(len(job_terms), 1)
        return round(min(75.0, coverage * 100), 2)

    @staticmethod
    def _explain(job: JobDescription, matched: list[str], missing: list[str], score: float) -> str:
        if score >= 85:
            strength = "strongly matches"
        elif score >= 70:
            strength = "is a solid match for"
        else:
            strength = "partially matches"
        matched_text = ", ".join(matched[:6]) or "the semantic profile"
        missing_text = f" Missing critical skills: {', '.join(missing[:4])}." if missing else ""
        return f"Candidate {strength} {job.title} with evidence around {matched_text}.{missing_text}"
