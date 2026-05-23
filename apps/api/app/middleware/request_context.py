from app.observability.tracing.middleware import TraceContextMiddleware

class RequestContextMiddleware(TraceContextMiddleware):
    """Backward-compatible alias for the consolidated trace context middleware."""
