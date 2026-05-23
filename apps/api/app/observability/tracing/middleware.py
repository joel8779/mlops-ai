from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import Request, Response
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.metrics import API_LATENCY
from app.observability.tracing.correlation import CorrelationContext, bind_correlation, enrich_span


class TraceContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        organization_id = request.headers.get("X-Organization-ID")
        recruiter_id = request.headers.get("X-Recruiter-ID")
        context = CorrelationContext(
            request_id=request_id,
            organization_id=organization_id,
            recruiter_id=recruiter_id,
        )
        structlog.contextvars.clear_contextvars()
        bind_correlation(context)
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("api.request_context") as span:
            span.set_attribute("http.route", request.url.path)
            span.set_attribute("http.method", request.method)
            enrich_span(context)
            with API_LATENCY.labels(request.method, request.url.path).time():
                response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            span.set_attribute("http.status_code", response.status_code)
            return response
