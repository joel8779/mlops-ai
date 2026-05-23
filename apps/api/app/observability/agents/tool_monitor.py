from app.observability.metrics import TOOL_INVOCATION_DURATION_MS


class ToolMonitor:
    def record_invocation(self, tool_name: str, status: str, duration_ms: float) -> None:
        TOOL_INVOCATION_DURATION_MS.labels(tool_name, status).observe(duration_ms)
