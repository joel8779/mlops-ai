from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
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
    """Configure OpenTelemetry tracing with graceful degradation."""
    global _configured
    if _configured:
        # Already configured, just instrument the app
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            FastAPIInstrumentor.instrument_app(app)
        except Exception:
            # Silently fail if instrumentation fails
            pass
        return

    try:
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
        
        # Instrument FastAPI
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
        except Exception:
            # Silently fail if FastAPI instrumentation fails
            pass
        
        # Instrument HTTPX
        try:
            from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
            HTTPXClientInstrumentor().instrument()
        except Exception:
            # Silently fail if HTTPX instrumentation fails
            pass
        
        # Instrument Redis
        try:
            from opentelemetry.instrumentation.redis import RedisInstrumentor
            RedisInstrumentor().instrument()
        except Exception:
            # Silently fail if Redis instrumentation fails
            pass
        
        # Instrument SQLAlchemy
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
        except Exception:
            # Silently fail if SQLAlchemy instrumentation fails
            pass
        
        _configured = True
    except Exception:
        # If tracing configuration fails completely, continue without tracing
        # This ensures the app can start even if telemetry is broken
        pass


def instrument_celery() -> None:
    """Instrument Celery with graceful degradation."""
    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
        CeleryInstrumentor().instrument()
    except Exception:
        # Silently fail if Celery instrumentation fails
        pass


@contextmanager
def traced_span(name: str, **attributes: Any) -> Iterator[Any]:
    """Create a traced span with graceful degradation."""
    try:
        with get_tracer(__name__).start_as_current_span(name) as span:
            for key, value in attributes.items():
                if value is not None:
                    span.set_attribute(key, str(value))
            yield span
    except Exception:
        # If tracing fails, continue without the span
        yield None
