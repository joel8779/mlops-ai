"""Metrics validation - Validate Prometheus metrics emission."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from prometheus_client import Counter, Histogram, Gauge, REGISTRY

from app.logging import get_logger


@dataclass
class MetricsValidationResult:
    """Result of metrics validation."""

    metric_count: int
    has_counter: bool
    has_histogram: bool
    has_gauge: bool
    registration_successful: bool
    error: Optional[str]
    timestamp: datetime


class MetricsValidator:
    """Validate Prometheus metrics emission."""

    def __init__(self) -> None:
        """Initialize metrics validator."""
        self.logger = get_logger(__name__)

    async def validate_metrics_emission(self) -> MetricsValidationResult:
        """Validate that metrics are emitted correctly.

        Returns:
            MetricsValidationResult
        """
        try:
            # Create test metrics
            test_counter = Counter("test_counter", "Test counter", ["label"])
            test_histogram = Histogram("test_histogram", "Test histogram")
            test_gauge = Gauge("test_gauge", "Test gauge")

            # Record some data
            test_counter.labels(label="test").inc()
            test_histogram.observe(1.0)
            test_gauge.set(42)

            # Check if metrics are registered
            metric_names = {sample.name for metric in REGISTRY.collect() for sample in metric.samples}

            has_counter = any("test_counter" in name for name in metric_names)
            has_histogram = any("test_histogram" in name for name in metric_names)
            has_gauge = any("test_gauge" in name for name in metric_names)

            # Clean up test metrics
            REGISTRY.unregister(test_counter)
            REGISTRY.unregister(test_histogram)
            REGISTRY.unregister(test_gauge)

            return MetricsValidationResult(
                metric_count=len(metric_names),
                has_counter=has_counter,
                has_histogram=has_histogram,
                has_gauge=has_gauge,
                registration_successful=True,
                error=None,
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as exc:
            return MetricsValidationResult(
                metric_count=0,
                has_counter=False,
                has_histogram=False,
                has_gauge=False,
                registration_successful=False,
                error=str(exc),
                timestamp=datetime.now(timezone.utc),
            )
