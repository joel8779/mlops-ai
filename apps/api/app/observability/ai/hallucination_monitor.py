from app.observability.metrics import AI_SAFETY_EVENTS_TOTAL


class HallucinationMonitor:
    def record_event(self, feature: str, severity: str, event_type: str = "hallucination") -> None:
        AI_SAFETY_EVENTS_TOTAL.labels(event_type, severity, feature).inc()
