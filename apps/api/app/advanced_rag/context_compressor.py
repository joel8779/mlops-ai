from app.schemas.matching import SemanticSearchResult


class ContextCompressor:
    def compress(self, results: list[SemanticSearchResult], max_chars: int = 6000) -> str:
        parts: list[str] = []
        used = 0
        for result in results:
            item = f"Candidate {result.candidate_id} | score={result.score}\n{result.snippet[:900]}"
            if used + len(item) > max_chars:
                break
            parts.append(item)
            used += len(item)
        return "\n\n".join(parts)
