from app.observability.metrics import (
    WEBSOCKET_ACTIVE_CONNECTIONS,
    WEBSOCKET_BROADCAST_LATENCY_MS,
    WEBSOCKET_DROPPED_CONNECTIONS_TOTAL,
)


class WebSocketMetrics:
    def set_active(self, organization_id: str, count: int) -> None:
        WEBSOCKET_ACTIVE_CONNECTIONS.labels(organization_id).set(count)

    def record_dropped(self, organization_id: str, reason: str) -> None:
        WEBSOCKET_DROPPED_CONNECTIONS_TOTAL.labels(organization_id, reason).inc()

    def record_broadcast_latency(self, organization_id: str, status: str, duration_ms: float) -> None:
        WEBSOCKET_BROADCAST_LATENCY_MS.labels(organization_id, status).observe(duration_ms)
