from __future__ import annotations

import logging

from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SpanExporter

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_span_exporter() -> SpanExporter | None:
    """Build span exporter with graceful degradation.

    Returns None if OTEL is disabled or exporter fails to initialize.
    Falls back to console exporter for local development.
    """
    # Global enable/disable flag
    if not settings.otel_enabled:
        logger.info("OpenTelemetry disabled via OTEL_ENABLED=false")
        return None

    exporter = settings.otel_traces_exporter.lower()
    if exporter == "none":
        return None
    if exporter == "console":
        return ConsoleSpanExporter()
    if exporter == "jaeger":
        try:
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        except ImportError as exc:
            logger.warning("Jaeger exporter not available, falling back to console: %s", exc)
            return ConsoleSpanExporter()
        try:
            return JaegerExporter(
                agent_host_name=settings.jaeger_agent_host,
                agent_port=settings.jaeger_agent_port,
            )
        except Exception as exc:
            logger.warning("Jaeger exporter initialization failed, falling back to console: %s", exc)
            return ConsoleSpanExporter()

    # OTLP exporter with safe initialization
    if exporter == "otlp":
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            # Create OTLP exporter with controlled retries
            return OTLPSpanExporter(
                endpoint=settings.otel_exporter_otlp_endpoint,
                timeout=10,  # 10 second timeout
            )
        except Exception as exc:
            logger.warning(
                "OTLP exporter initialization failed, falling back to console: %s",
                exc,
            )
            return ConsoleSpanExporter()

    # Unknown exporter, fall back to console
    logger.warning("Unknown exporter type '%s', falling back to console", exporter)
    return ConsoleSpanExporter()
