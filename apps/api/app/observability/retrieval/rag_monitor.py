from app.observability.metrics import AI_SAFETY_EVENTS_TOTAL


class RAGMonitor:
    def record_grounding_check(self, feature: str, grounded: bool) -> None:
        severity = "info" if grounded else "warning"
        AI_SAFETY_EVENTS_TOTAL.labels("grounding_check", severity, feature).inc()
