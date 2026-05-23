"""Metadata Reranker - Rerank results based on metadata filters."""

from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.domain import Candidate
from app.services.retrieval.hybrid_retriever import RetrievalResult


@dataclass
class RerankConfig:
    """Configuration for reranking."""

    location_boost: float = 0.1
    experience_boost: float = 0.15
    skill_boost: float = 0.2
    recent_activity_boost: float = 0.05


class MetadataReranker:
    """Rerank search results based on metadata."""

    def __init__(
        self,
        db: AsyncSession,
        config: Optional[RerankConfig] = None,
    ) -> None:
        """Initialize metadata reranker.

        Args:
            db: Database session
            config: Optional rerank configuration
        """
        self.db = db
        self.config = config or RerankConfig()

    async def rerank(
        self,
        results: list[RetrievalResult],
        filters: dict[str, Any],
        limit: int,
    ) -> list[RetrievalResult]:
        """Rerank results based on metadata filters.

        Args:
            results: Initial search results
            filters: Metadata filters
            limit: Number of results to return

        Returns:
            Reranked list of RetrievalResult objects
        """
        if not results:
            return results

        # Get candidate IDs
        candidate_ids = [r.candidate_id for r in results]

        # Fetch candidate metadata
        candidates = await self._fetch_candidates(candidate_ids)

        # Apply reranking
        reranked = []
        for result in results:
            candidate = candidates.get(result.candidate_id)
            if not candidate:
                continue

            # Calculate boost
            boost = self._calculate_boost(candidate, filters)

            # Apply boost to score
            adjusted_score = result.score * (1 + boost)

            reranked.append(
                RetrievalResult(
                    candidate_id=result.candidate_id,
                    score=adjusted_score,
                    vector_score=result.vector_score,
                    keyword_score=result.keyword_score,
                    metadata={
                        **(result.metadata or {}),
                        "rerank_boost": boost,
                    },
                )
            )

        # Sort by adjusted score
        reranked.sort(key=lambda x: x.score, reverse=True)

        return reranked[:limit]

    async def _fetch_candidates(self, candidate_ids: list[UUID]) -> dict[UUID, Candidate]:
        """Fetch candidates by IDs.

        Args:
            candidate_ids: List of candidate IDs

        Returns:
            Dictionary mapping IDs to Candidate objects
        """
        query = select(Candidate).where(Candidate.id.in_(candidate_ids))
        result = await self.db.execute(query)
        candidates = result.scalars().all()

        return {c.id: c for c in candidates}

    def _calculate_boost(self, candidate: Candidate, filters: dict[str, Any]) -> float:
        """Calculate reranking boost for a candidate.

        Args:
            candidate: Candidate object
            filters: Filter criteria

        Returns:
            Boost value
        """
        boost = 0.0

        # Location boost
        if filters.get("location"):
            if candidate.location and filters["location"].lower() in candidate.location.lower():
                boost += self.config.location_boost

        # Experience boost
        if filters.get("min_experience"):
            # This would need actual experience data from the candidate
            # For now, apply a small boost if candidate has experience
            boost += self.config.experience_boost * 0.5

        # Skill boost
        if filters.get("required_skills"):
            # This would need actual skill matching
            # For now, apply a small boost
            boost += self.config.skill_boost * 0.3

        # Recent activity boost
        # This would need activity timestamp data
        boost += self.config.recent_activity_boost

        return boost
