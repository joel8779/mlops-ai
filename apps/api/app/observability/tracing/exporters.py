from __future__ import annotations

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SpanExporter

from app.core.config import settings


def build_span_exporter() -> SpanExporter | None:
    exporter = settings.otel_traces_exporter.lower()
    if exporter == "none":
        return None
    if exporter == "console":
        return ConsoleSpanExporter()
    if exporter == "jaeger":
        try:
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        except ImportError as exc:
            raise RuntimeError("Install opentelemetry-exporter-jaeger to use OTEL_TRACES_EXPORTER=jaeger") from exc
        return JaegerExporter(
            agent_host_name=settings.jaeger_agent_host,
            agent_port=settings.jaeger_agent_port,
        )
    return OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
