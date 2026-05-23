"""Hybrid Retriever - Combine vector and keyword search for optimal results."""

from dataclasses import dataclass
from enum import Enum
from time import perf_counter
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.retrieval.bm25_indexer import BM25Indexer
from app.services.retrieval.reranker import MetadataReranker
from app.services.semantic_search_service import SemanticSearchService
from app.observability.metrics import (
    RETRIEVAL_LATENCY,
    RETRIEVAL_RESULT_COUNT,
    RETRIEVAL_TOPK_LATENCY_MS,
    elapsed_ms,
)
from app.observability.tracing import get_tracer


tracer = get_tracer(__name__)


class FusionMethod(str, Enum):
    """Methods for fusing vector and keyword results."""

    RRF = "rrf"  # Reciprocal Rank Fusion
    WEIGHTED = "weighted"  # Weighted linear combination
    CASCADE = "cascade"  # Vector first, then keyword


@dataclass
class RetrievalResult:
    """Result from hybrid retrieval."""

    candidate_id: UUID
    score: float
    vector_score: Optional[float] = None
    keyword_score: Optional[float] = None
    metadata: dict[str, Any] = None


class HybridRetriever:
    """Hybrid retrieval combining vector and keyword search."""

    def __init__(
        self,
        db: AsyncSession,
        vector_weight: float = 0.6,
        keyword_weight: float = 0.4,
        fusion_method: FusionMethod = FusionMethod.RRF,
    ) -> None:
        """Initialize hybrid retriever.

        Args:
            db: Database session
            vector_weight: Weight for vector search results
            keyword_weight: Weight for keyword search results
            fusion_method: Method for fusing results
        """
        self.db = db
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        self.fusion_method = fusion_method
        self.semantic_search = SemanticSearchService(db)
        self.bm25_indexer = BM25Indexer(db)
        self.reranker = MetadataReranker(db)

    async def search(
        self,
        query: str,
        organization_id: UUID,
        job_description_id: Optional[UUID] = None,
        limit: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Perform hybrid search.

        Args:
            query: Search query
            organization_id: Organization ID
            job_description_id: Optional job description ID
            limit: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of RetrievalResult objects
        """
        filters = filters or {}
        strategy = self.fusion_method.value
        start_time = perf_counter()

        try:
            with tracer.start_as_current_span("retrieval.hybrid_search") as span:
                span.set_attribute("retrieval.strategy", strategy)
                span.set_attribute("retrieval.limit", limit)
                span.set_attribute("organization.id", str(organization_id))

                vector_results = await self.semantic_search.search_candidates(
                    organization_id=organization_id,
                    query=query,
                    job_description_id=job_description_id,
                    limit=limit * 2,
                )
                keyword_results = await self.bm25_indexer.search(
                    query=query,
                    organization_id=organization_id,
                    job_description_id=job_description_id,
                    limit=limit * 2,
                )
                fused_results = self._fuse_results(
                    vector_results,
                    keyword_results,
                    limit=limit * 2,
                )
                reranked = await self.reranker.rerank(
                    results=fused_results,
                    filters=filters,
                    limit=limit,
                )
                span.set_attribute("retrieval.result_count", len(reranked))
        except Exception:
            duration_ms = elapsed_ms(start_time)
            RETRIEVAL_TOPK_LATENCY_MS.labels(strategy, "error").observe(duration_ms)
            RETRIEVAL_LATENCY.labels(strategy).observe(duration_ms / 1000)
            raise

        duration_ms = elapsed_ms(start_time)
        RETRIEVAL_TOPK_LATENCY_MS.labels(strategy, "success").observe(duration_ms)
        RETRIEVAL_LATENCY.labels(strategy).observe(duration_ms / 1000)
        RETRIEVAL_RESULT_COUNT.labels(strategy).observe(len(reranked))
        return reranked

    def _fuse_results(
        self,
        vector_results: list[Any],
        keyword_results: list[Any],
        limit: int,
    ) -> list[RetrievalResult]:
        """Fuse vector and keyword results.

        Args:
            vector_results: Vector search results
            keyword_results: Keyword search results
            limit: Number of results to return

        Returns:
            Fused list of RetrievalResult objects
        """
        if self.fusion_method == FusionMethod.RRF:
            return self._rrf_fusion(vector_results, keyword_results, limit)
        elif self.fusion_method == FusionMethod.WEIGHTED:
            return self._weighted_fusion(vector_results, keyword_results, limit)
        else:  # CASCADE
            return self._cascade_fusion(vector_results, keyword_results, limit)

    def _rrf_fusion(
        self,
        vector_results: list[Any],
        keyword_results: list[Any],
        limit: int,
        k: int = 60,
    ) -> list[RetrievalResult]:
        """Reciprocal Rank Fusion.

        Args:
            vector_results: Vector search results
            keyword_results: Keyword search results
            limit: Number of results
            k: RRF constant

        Returns:
            Fused results
        """
        scores = {}

        # Score vector results
        for rank, result in enumerate(vector_results, 1):
            candidate_id = getattr(result, "id", None)
            if candidate_id:
                scores[candidate_id] = scores.get(candidate_id, 0) + 1 / (k + rank)

        # Score keyword results
        for rank, result in enumerate(keyword_results, 1):
            candidate_id = getattr(result, "id", None)
            if candidate_id:
                scores[candidate_id] = scores.get(candidate_id, 0) + 1 / (k + rank)

        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [
            RetrievalResult(
                candidate_id=candidate_id,
                score=score,
                metadata={"fusion_method": "rrf"},
            )
            for candidate_id, score in sorted_results[:limit]
        ]

    def _weighted_fusion(
        self,
        vector_results: list[Any],
        keyword_results: list[Any],
        limit: int,
    ) -> list[RetrievalResult]:
        """Weighted linear combination fusion.

        Args:
            vector_results: Vector search results
            keyword_results: Keyword search results
            limit: Number of results

        Returns:
            Fused results
        """
        scores = {}

        # Score vector results
        for result in vector_results:
            candidate_id = getattr(result, "id", None)
            vector_score = getattr(result, "score", 0.5)
            if candidate_id:
                scores[candidate_id] = scores.get(candidate_id, 0) + vector_score * self.vector_weight

        # Score keyword results
        for result in keyword_results:
            candidate_id = getattr(result, "id", None)
            keyword_score = getattr(result, "score", 0.5)
            if candidate_id:
                scores[candidate_id] = scores.get(candidate_id, 0) + keyword_score * self.keyword_weight

        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [
            RetrievalResult(
                candidate_id=candidate_id,
                score=score,
                metadata={"fusion_method": "weighted"},
            )
            for candidate_id, score in sorted_results[:limit]
        ]

    def _cascade_fusion(
        self,
        vector_results: list[Any],
        keyword_results: list[Any],
        limit: int,
    ) -> list[RetrievalResult]:
        """Cascade fusion - vector first, then keyword to fill gaps.

        Args:
            vector_results: Vector search results
            keyword_results: Keyword search results
            limit: Number of results

        Returns:
            Fused results
        """
        seen_ids = set()
        results = []

        # Add vector results first
        for result in vector_results:
            candidate_id = getattr(result, "id", None)
            if candidate_id and candidate_id not in seen_ids:
                results.append(
                    RetrievalResult(
                        candidate_id=candidate_id,
                        score=getattr(result, "score", 0.5),
                        vector_score=getattr(result, "score", 0.5),
                        metadata={"fusion_method": "cascade"},
                    )
                )
                seen_ids.add(candidate_id)

        # Fill with keyword results
        for result in keyword_results:
            candidate_id = getattr(result, "id", None)
            if candidate_id and candidate_id not in seen_ids and len(results) < limit:
                results.append(
                    RetrievalResult(
                        candidate_id=candidate_id,
                        score=getattr(result, "score", 0.5),
                        keyword_score=getattr(result, "score", 0.5),
                        metadata={"fusion_method": "cascade"},
                    )
                )
                seen_ids.add(candidate_id)

        return results[:limit]
