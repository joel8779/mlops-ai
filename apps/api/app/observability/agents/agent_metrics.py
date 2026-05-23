from app.observability.metrics import AGENT_EXECUTION_FAILURES_TOTAL, AGENT_STEP_LATENCY_MS, AUTONOMOUS_ACTIONS_TOTAL


class AgentMetrics:
    def record_step_latency(self, step: str, status: str, duration_ms: float) -> None:
        AGENT_STEP_LATENCY_MS.labels(step, status).observe(duration_ms)

    def record_failure(self, step: str, error_type: str) -> None:
        AGENT_EXECUTION_FAILURES_TOTAL.labels(step, error_type).inc()

    def record_action(self, action: str, outcome: str) -> None:
        AUTONOMOUS_ACTIONS_TOTAL.labels(action, outcome).inc()
