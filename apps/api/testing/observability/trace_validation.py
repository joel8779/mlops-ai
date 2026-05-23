"""Trace validation - Validate OpenTelemetry trace emission."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from app.logging import get_logger


@dataclass
class TraceValidationResult:
    """Result of trace validation."""

    span_count: int
    has_parent_span: bool
    has_attributes: bool
    has_events: bool
    export_successful: bool
    error: Optional[str]
    timestamp: datetime


class TraceValidator:
    """Validate OpenTelemetry trace emission."""

    def __init__(self) -> None:
        """Initialize trace validator."""
        self.logger = get_logger(__name__)
        self.exporter = InMemorySpanExporter()
        self.provider = TracerProvider()
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))

    async def validate_trace_emission(self) -> TraceValidationResult:
        """Validate that traces are emitted correctly.

        Returns:
            TraceValidationResult
        """
        try:
            tracer = trace.get_tracer(__name__, tracer_provider=self.provider)

            with tracer.start_as_current_span("test_span") as parent:
                parent.set_attribute("test_attribute", "test_value")
                parent.add_event("test_event", {"key": "value"})

                with tracer.start_as_current_span("child_span") as child:
                    child.set_attribute("child_attribute", "child_value")

            # Get exported spans
            spans = self.exporter.get_finished_spans()

            if not spans:
                return TraceValidationResult(
                    span_count=0,
                    has_parent_span=False,
                    has_attributes=False,
                    has_events=False,
                    export_successful=False,
                    error="No spans exported",
                    timestamp=datetime.now(timezone.utc),
                )

            has_parent = any(span.parent for span in spans)
            has_attributes = any(span.attributes for span in spans)
            has_events = any(span.events for span in spans)

            return TraceValidationResult(
                span_count=len(spans),
                has_parent_span=has_parent,
                has_attributes=has_attributes,
                has_events=has_events,
                export_successful=True,
                error=None,
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as exc:
            return TraceValidationResult(
                span_count=0,
                has_parent_span=False,
                has_attributes=False,
                has_events=False,
                export_successful=False,
                error=str(exc),
                timestamp=datetime.now(timezone.utc),
            )

    def clear_spans(self) -> None:
        """Clear exported spans."""
        self.exporter.clear()
