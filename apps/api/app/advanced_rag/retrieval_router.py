from dataclasses import dataclass
from uuid import UUID

from app.schemas.matching import SemanticSearchRequest, SemanticSearchResult
from app.services.semantic_search_service import SemanticSearchService


@dataclass(frozen=True)
class RetrievalPlan:
    rewritten_query: str
    strategy: str
    top_k: int


class RetrievalRouter:
    def plan(self, query: str, top_k: int) -> RetrievalPlan:
        normalized = query.strip()
        strategy = "hybrid_bm25_vector" if len(normalized.split()) > 3 else "vector"
        rewritten = self._rewrite(normalized)
        return RetrievalPlan(rewritten_query=rewritten, strategy=strategy, top_k=top_k)

    def retrieve(self, organization_id: UUID, owner_id: UUID, plan: RetrievalPlan) -> list[SemanticSearchResult]:
        return SemanticSearchService().raw_chunk_search(
            organization_id,
            owner_id,
            SemanticSearchRequest(query=plan.rewritten_query, limit=plan.top_k),
        )

    @staticmethod
    def _rewrite(query: str) -> str:
        replacements = {"backend": "backend API FastAPI PostgreSQL", "ml": "machine learning NLP PyTorch"}
        lowered = query.lower()
        expansions = [value for key, value in replacements.items() if key in lowered]
        return f"{query} {' '.join(expansions)}".strip()
