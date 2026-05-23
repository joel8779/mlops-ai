from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import structlog
from opentelemetry import trace


@dataclass(frozen=True)
class CorrelationContext:
    request_id: str | None = None
    organization_id: UUID | str | None = None
    recruiter_id: UUID | str | None = None
    session_id: UUID | str | None = None

    def as_log_context(self) -> dict[str, str]:
        values = {
            "request_id": self.request_id,
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "recruiter_id": str(self.recruiter_id) if self.recruiter_id else None,
            "session_id": str(self.session_id) if self.session_id else None,
        }
        return {key: value for key, value in values.items() if value}


def current_trace_context() -> dict[str, str]:
    span_context = trace.get_current_span().get_span_context()
    if not span_context.is_valid:
        return {}
    return {
        "trace_id": format(span_context.trace_id, "032x"),
        "span_id": format(span_context.span_id, "016x"),
    }


def bind_correlation(context: CorrelationContext) -> None:
    structlog.contextvars.bind_contextvars(**context.as_log_context())


def enrich_span(context: CorrelationContext) -> None:
    span = trace.get_current_span()
    if not span.is_recording():
        return
    for key, value in context.as_log_context().items():
        span.set_attribute(key.replace("_", "."), value)
