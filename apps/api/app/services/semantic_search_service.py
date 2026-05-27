from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import ATSScore, Candidate, CandidateMatch, Resume
from app.repositories.candidates import CandidateRepository
from app.repositories.jobs import JobDescriptionRepository
from app.schemas.matching import CandidateSearchResult, SemanticSearchRequest, SemanticSearchResult
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService


@dataclass(frozen=True)
class CandidateSearchHit:
    id: UUID
    score: float
    metadata: dict[str, Any]

    @property
    def full_name(self) -> str | None:
        return self.metadata.get("full_name")

    @property
    def headline(self) -> str | None:
        return self.metadata.get("headline")

    @property
    def location(self) -> str | None:
        return self.metadata.get("location")


class SemanticSearchService:
    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db

    async def search(self, organization_id: UUID, owner_id: UUID, payload: SemanticSearchRequest) -> list[CandidateSearchResult]:
        if self.db is None:
            raise RuntimeError("Candidate-level semantic search requires a database session")
        await self._ensure_job_context(organization_id, owner_id, payload.job_description_id)
        try:
            hits = EmbeddingService().candidate_search(
                organization_id=organization_id,
                owner_id=owner_id,
                query=payload.query,
                limit=min(payload.limit * 5 + payload.offset, 100),
                skills=payload.skills,
            )
        except Exception:
            hits = []
        aggregated = self._aggregate_hits(hits, payload)
        repository = CandidateRepository(self.db)
        if not aggregated:
            aggregated = await self._database_fallback(repository, organization_id, owner_id, payload)
        candidate_ids = list(aggregated.keys())[payload.offset : payload.offset + payload.limit]
        results: list[CandidateSearchResult] = []
        for candidate_id in candidate_ids:
            candidate = await repository.get_for_owner(candidate_id, organization_id, owner_id)
            if candidate is None:
                continue
            if payload.location and payload.location.lower() not in str(candidate.location or "").lower():
                continue
            resume = await repository.latest_resume(candidate.id, organization_id, owner_id)
            skills = await repository.skills_for_candidate(candidate.id, organization_id, owner_id)
            match = await self._job_match(organization_id, owner_id, candidate.id, payload.job_description_id)
            ats_score = await self._ats_score(organization_id, owner_id, candidate.id, payload.job_description_id)
            matched_skills = match.matched_skills if match else self._matched_query_skills(payload.query, skills)
            missing_skills = match.missing_skills if match else []
            semantic_score = max(aggregated[candidate_id]["score"], float(match.semantic_score) if match else 0)
            results.append(
                CandidateSearchResult(
                    candidate_id=candidate.id,
                    full_name=candidate.full_name,
                    headline=candidate.headline,
                    location=candidate.location,
                    latest_resume_id=resume.id if resume else None,
                    semantic_score=round(semantic_score, 2),
                    ats_alignment=float(ats_score) if ats_score is not None else (float(match.overall_score) if match else None),
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    experience_fit=float(match.experience_match) if match else None,
                    summary=candidate.summary or self._resume_summary(resume),
                    overlap_reasoning=self._reasoning(payload.query, candidate, matched_skills, aggregated[candidate_id]["snippets"]),
                )
            )
        return sorted(
            results,
            key=lambda item: (item.ats_alignment or 0, item.semantic_score, item.experience_fit or 0),
            reverse=True,
        )

    async def _ensure_job_context(self, organization_id: UUID, owner_id: UUID, job_id: UUID | None) -> None:
        if job_id is None or self.db is None:
            return
        existing = await self.db.scalar(
            select(CandidateMatch.id).where(
                CandidateMatch.organization_id == organization_id,
                CandidateMatch.owner_id == owner_id,
                CandidateMatch.job_description_id == job_id,
            ).limit(1)
        )
        if existing is not None:
            return
        job = await JobDescriptionRepository(self.db).get_for_owner(job_id, organization_id, owner_id)
        if job is not None:
            await MatchingService(self.db).rank_candidates(organization_id, owner_id, job, limit=100)

    async def _database_fallback(
        self,
        repository: CandidateRepository,
        organization_id: UUID,
        owner_id: UUID,
        payload: SemanticSearchRequest,
    ) -> dict[UUID, dict[str, Any]]:
        candidates = await repository.list_for_owner(organization_id, owner_id, limit=min(payload.limit * 5 + payload.offset, 100))
        terms = {term.lower() for term in payload.query.split() if len(term) > 2}
        fallback: dict[UUID, dict[str, Any]] = {}
        for candidate in candidates:
            resume = await repository.latest_resume(candidate.id, organization_id, owner_id)
            skills = await repository.skills_for_candidate(candidate.id, organization_id, owner_id)
            text = " ".join(
                [
                    candidate.full_name or "",
                    candidate.headline or "",
                    candidate.summary or "",
                    " ".join(skills),
                    (resume.extracted_text if resume else "") or "",
                ]
            ).lower()
            score = sum(1 for term in terms if term in text) * 12.5
            match = await self._job_match(organization_id, owner_id, candidate.id, payload.job_description_id)
            if match:
                score = max(score, float(match.semantic_score), float(match.overall_score) * 0.6)
            if payload.skills and not set(payload.skills) & set(skills):
                continue
            if score > 0 or match:
                fallback[candidate.id] = {
                    "score": min(100.0, score),
                    "snippets": [((resume.extracted_text if resume else "") or candidate.summary or "")[:220]],
                    "payload": {"candidate_id": str(candidate.id)},
                }
        return dict(sorted(fallback.items(), key=lambda item: item[1]["score"], reverse=True))

    def raw_chunk_search(self, organization_id: UUID, owner_id: UUID, payload: SemanticSearchRequest) -> list[SemanticSearchResult]:
        hits = EmbeddingService().candidate_search(
            organization_id=organization_id,
            owner_id=owner_id,
            query=payload.query,
            limit=payload.limit + payload.offset,
            skills=payload.skills,
        )
        page = hits[payload.offset : payload.offset + payload.limit]
        return [
            SemanticSearchResult(
                candidate_id=UUID(hit["payload"]["candidate_id"]),
                resume_id=UUID(hit["payload"]["resume_id"]) if hit["payload"].get("resume_id") else None,
                score=round(hit["score"] * 100, 2),
                snippet=str(hit["payload"].get("text", ""))[:500],
                payload=hit["payload"],
            )
            for hit in page
            if hit.get("payload", {}).get("candidate_id")
        ]

    async def search_candidates(
        self,
        organization_id: UUID,
        owner_id: UUID,
        query: str,
        job_description_id: UUID | None = None,
        limit: int = 10,
    ) -> list[CandidateSearchHit]:
        payload = SemanticSearchRequest(query=query, job_description_id=job_description_id, limit=limit)
        return [
            CandidateSearchHit(
                id=result.candidate_id,
                score=result.semantic_score / 100,
                metadata=result.model_dump(),
            )
            for result in await self.search(organization_id, owner_id, payload)
        ]

    @staticmethod
    def _aggregate_hits(hits: list[dict], payload: SemanticSearchRequest) -> dict[UUID, dict[str, Any]]:
        terms = {term.lower() for term in payload.query.split() if len(term) > 2}
        aggregated: dict[UUID, dict[str, Any]] = {}
        for hit in hits:
            data = hit.get("payload") or {}
            candidate_id = data.get("candidate_id")
            if not candidate_id:
                continue
            key = UUID(candidate_id)
            snippet = str(data.get("text", ""))
            lexical_boost = sum(1 for term in terms if term in snippet.lower()) * 1.5
            score = min(100.0, float(hit.get("score", 0)) * 100 + lexical_boost)
            current = aggregated.setdefault(key, {"score": 0.0, "snippets": [], "payload": data})
            current["score"] = max(current["score"], score)
            if snippet:
                current["snippets"].append(snippet[:220])
        return dict(sorted(aggregated.items(), key=lambda item: item[1]["score"], reverse=True))

    async def _job_match(self, organization_id: UUID, owner_id: UUID, candidate_id: UUID, job_id: UUID | None) -> CandidateMatch | None:
        if job_id is None or self.db is None:
            return None
        return await self.db.scalar(
            select(CandidateMatch)
            .where(
                CandidateMatch.organization_id == organization_id,
                CandidateMatch.owner_id == owner_id,
                CandidateMatch.candidate_id == candidate_id,
                CandidateMatch.job_description_id == job_id,
            )
            .order_by(desc(CandidateMatch.updated_at))
            .limit(1)
        )

    async def _ats_score(self, organization_id: UUID, owner_id: UUID, candidate_id: UUID, job_id: UUID | None):
        if job_id is None or self.db is None:
            return None
        return await self.db.scalar(
            select(ATSScore.ats_score)
            .where(
                ATSScore.organization_id == organization_id,
                ATSScore.owner_id == owner_id,
                ATSScore.candidate_id == candidate_id,
                ATSScore.job_description_id == job_id,
            )
            .order_by(desc(ATSScore.updated_at))
            .limit(1)
        )

    @staticmethod
    def _matched_query_skills(query: str, skills: list[str]) -> list[str]:
        lower = query.lower()
        return [skill for skill in skills if skill.lower() in lower]

    @staticmethod
    def _resume_summary(resume: Resume | None) -> str | None:
        if not resume or not resume.extracted_text:
            return None
        text = " ".join(resume.extracted_text.split())
        return text[:260]

    @staticmethod
    def _reasoning(query: str, candidate: Candidate, skills: list[str], snippets: list[str]) -> str:
        if skills:
            return f"Matched query '{query}' through candidate skills: {', '.join(skills[:6])}."
        if snippets:
            return f"Matched query '{query}' through resume evidence: {snippets[0][:180]}."
        return f"Matched query '{query}' through semantic similarity to {candidate.full_name or 'this candidate'}."
