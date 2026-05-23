from app.observability.metrics import (
    REDIS_STREAM_CONSUMER_LAG,
    REDIS_STREAM_EVENTS_CONSUMED_TOTAL,
    REDIS_STREAM_EVENTS_PUBLISHED_TOTAL,
    REDIS_STREAM_PROCESSING_LATENCY_MS,
)


class StreamMonitor:
    def record_lag(self, stream: str, consumer_group: str, pending: int) -> None:
        REDIS_STREAM_CONSUMER_LAG.labels(stream, consumer_group).set(pending)

    def record_published(self, stream: str, event_type: str) -> None:
        REDIS_STREAM_EVENTS_PUBLISHED_TOTAL.labels(stream, event_type).inc()

    def record_consumed(self, stream: str, consumer_group: str, event_type: str, status: str) -> None:
        REDIS_STREAM_EVENTS_CONSUMED_TOTAL.labels(stream, consumer_group, event_type, status).inc()

    def record_processing_latency(self, stream: str, consumer_group: str, event_type: str, status: str, duration_ms: float) -> None:
        REDIS_STREAM_PROCESSING_LATENCY_MS.labels(stream, consumer_group, event_type, status).observe(duration_ms)
