from app.observability.metrics import (
    RETRIEVAL_CACHE_HITS_TOTAL,
    RETRIEVAL_CACHE_MISSES_TOTAL,
    RETRIEVAL_CONFIDENCE,
    RETRIEVAL_RESULT_COUNT,
    RETRIEVAL_SIMILARITY_SCORE,
    RETRIEVAL_TOPK_LATENCY_MS,
)


class RetrievalMetrics:
    def record_latency(self, strategy: str, status: str, duration_ms: float) -> None:
        RETRIEVAL_TOPK_LATENCY_MS.labels(strategy, status).observe(duration_ms)

    def record_results(self, strategy: str, count: int, confidence: float | None = None) -> None:
        RETRIEVAL_RESULT_COUNT.labels(strategy).observe(count)
        if confidence is not None:
            RETRIEVAL_CONFIDENCE.labels(strategy).observe(confidence)

    def record_similarity(self, strategy: str, score: float) -> None:
        RETRIEVAL_SIMILARITY_SCORE.labels(strategy).observe(score)

    def record_cache(self, cache_name: str, hit: bool) -> None:
        metric = RETRIEVAL_CACHE_HITS_TOTAL if hit else RETRIEVAL_CACHE_MISSES_TOTAL
        metric.labels(cache_name).inc()
