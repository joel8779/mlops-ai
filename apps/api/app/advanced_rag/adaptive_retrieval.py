"""Intent-aware retrieval with query expansion, personalized reranking, and confidence scoring."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.personalization.preference_model import RecruiterPreferenceModel
from app.knowledge_graph.taxonomy.taxonomy_service import TaxonomyService
from app.services.retrieval.hybrid_retriever import HybridRetriever, RetrievalResult


@dataclass(frozen=True)
class AdaptiveRetrievalResponse:
    rewritten_query: str
    results: list[RetrievalResult]
    confidence: float
    diagnostics: dict[str, Any] = field(default_factory=dict)


class AdaptiveRetrievalEngine:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.taxonomy = TaxonomyService()
        self.preferences = RecruiterPreferenceModel(db)

    async def search(
        self,
        organization_id: UUID,
        recruiter_id: UUID,
        query: str,
        limit: int = 10,
        context: dict[str, Any] | None = None,
    ) -> AdaptiveRetrievalResponse:
        context = context or {}
        rewritten = self._rewrite(query, context)
        retriever = HybridRetriever(self.db)
        results = await retriever.search(rewritten, organization_id, recruiter_id, context.get("job_id"), limit=limit)
        profile = await self.preferences.build_profile(organization_id, recruiter_id)
        reranked = self._personalize(results, profile.skill_weights)
        confidence = self._confidence(reranked, rewritten)
        return AdaptiveRetrievalResponse(
            rewritten_query=rewritten,
            results=reranked,
            confidence=confidence,
            diagnostics={"preference_confidence": profile.confidence, "result_count": len(reranked)},
        )

    def _rewrite(self, query: str, context: dict[str, Any]) -> str:
        skills = context.get("skills", [])
        expanded = self.taxonomy.skills.expand(skills) if skills else []
        return " ".join([query.strip(), *expanded]).strip()

    @staticmethod
    def _personalize(results: list[RetrievalResult], skill_weights: dict[str, float]) -> list[RetrievalResult]:
        for result in results:
            metadata = result.metadata or {}
            skills = [str(skill).lower() for skill in metadata.get("skills", [])]
            boost = sum(skill_weights.get(skill, 0.0) for skill in skills)
            result.score = round(float(result.score) + boost, 6)
            result.metadata = {**metadata, "personalization_boost": round(boost, 6)}
        return sorted(results, key=lambda item: item.score, reverse=True)

    @staticmethod
    def _confidence(results: list[RetrievalResult], query: str) -> float:
        if not results:
            return 0.0
        top_score = float(results[0].score)
        spread = top_score - float(results[min(len(results) - 1, 4)].score)
        query_specificity = min(0.2, len(query.split()) / 50)
        return round(max(0.05, min(0.99, 0.45 + spread + query_specificity)), 3)
