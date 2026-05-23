from app.observability.metrics import WEBSOCKET_BROADCAST_LATENCY_MS


class PubSubMetrics:
    def record_publish_latency(self, channel: str, status: str, duration_ms: float) -> None:
        WEBSOCKET_BROADCAST_LATENCY_MS.labels(channel, status).observe(duration_ms)
