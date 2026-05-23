from app.schemas.matching import SemanticSearchResult


class RAGRerankingService:
    def rerank(self, query: str, results: list[SemanticSearchResult]) -> list[SemanticSearchResult]:
        query_terms = {term.lower() for term in query.split() if len(term) > 2}
        for result in results:
            text = result.snippet.lower()
            coverage = sum(1 for term in query_terms if term in text) / max(len(query_terms), 1)
            result.score = round(min(100.0, result.score * 0.85 + coverage * 15), 2)
        return sorted(results, key=lambda item: item.score, reverse=True)
