from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings
from app.db.session import engine
from app.observability.tracing.exporters import build_span_exporter

_configured = False


def get_tracer(name: str):
    return trace.get_tracer(name)


def configure_tracing(app: FastAPI) -> None:
    global _configured
    if _configured:
        FastAPIInstrumentor.instrument_app(app)
        return

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": settings.otel_service_name,
                "service.version": settings.app_version,
                "deployment.environment": settings.environment,
            }
        )
    )
    exporter = build_span_exporter()
    if exporter is not None:
        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    HTTPXClientInstrumentor().instrument()
    RedisInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    _configured = True


def instrument_celery() -> None:
    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
    except ImportError:
        return
    CeleryInstrumentor().instrument()


@contextmanager
def traced_span(name: str, **attributes: Any) -> Iterator[Any]:
    with get_tracer(__name__).start_as_current_span(name) as span:
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(key, str(value))
        yield span
