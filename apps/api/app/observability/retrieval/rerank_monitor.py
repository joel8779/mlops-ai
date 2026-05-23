from app.observability.metrics import RANKING_LATENCY


class RerankMonitor:
    def record_latency(self, version: str, duration_seconds: float) -> None:
        RANKING_LATENCY.labels(version).observe(duration_seconds)
