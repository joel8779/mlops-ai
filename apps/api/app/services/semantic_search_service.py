from uuid import UUID

from app.schemas.matching import SemanticSearchRequest, SemanticSearchResult
from app.services.embedding_service import EmbeddingService


class SemanticSearchService:
    def search(self, organization_id: UUID, payload: SemanticSearchRequest) -> list[SemanticSearchResult]:
        hits = EmbeddingService().candidate_search(
            organization_id=organization_id,
            query=payload.query,
            limit=payload.limit + payload.offset,
            skills=payload.skills,
        )
        page = hits[payload.offset : payload.offset + payload.limit]
        results: list[SemanticSearchResult] = []
        for hit in page:
            data = hit["payload"]
            if payload.location and payload.location.lower() not in str(data.get("location", "")).lower():
                continue
            results.append(
                SemanticSearchResult(
                    candidate_id=UUID(data["candidate_id"]),
                    resume_id=UUID(data["resume_id"]) if data.get("resume_id") else None,
                    score=round(hit["score"] * 100, 2),
                    snippet=str(data.get("text", ""))[:500],
                    payload=data,
                )
            )
        return self._rerank(payload.query, results)

    @staticmethod
    def _rerank(query: str, results: list[SemanticSearchResult]) -> list[SemanticSearchResult]:
        terms = {term.lower() for term in query.split() if len(term) > 2}
        for result in results:
            snippet_terms = result.snippet.lower()
            lexical_boost = sum(1 for term in terms if term in snippet_terms) * 1.5
            result.score = round(min(100.0, result.score + lexical_boost), 2)
        return sorted(results, key=lambda item: item.score, reverse=True)
