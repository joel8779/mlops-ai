"""Observability validator - Validate observability stack."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from prometheus_client import REGISTRY

from app.logging import get_logger


class ObservabilityStatus(str, Enum):
    """Observability validation status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


@dataclass
class ObservabilityCheck:
    """Result of an observability check."""

    name: str
    status: ObservabilityStatus
    message: str
    details: dict[str, Any]
    timestamp: datetime


class ObservabilityValidator:
    """Validate observability stack."""

    def __init__(self) -> None:
        """Initialize observability validator."""
        self.logger = get_logger(__name__)
        self.checks: list[ObservabilityCheck] = []

    async def validate_all(self) -> list[ObservabilityCheck]:
        """Validate all observability components.

        Returns:
            List of ObservabilityCheck objects
        """
        self.logger.info("observability_validation_beginning")

        validations = [
            self._check_metrics_registry,
            self._check_required_metrics,
            self._check_logging_configured,
        ]

        for validation in validations:
            try:
                result = await validation()
                self.checks.append(result)
            except Exception as exc:
                self.logger.exception("observability_check_failed", check=validation.__name__)
                self.checks.append(
                    ObservabilityCheck(
                        name=validation.__name__,
                        status=ObservabilityStatus.UNHEALTHY,
                        message=f"Check failed: {exc}",
                        details={"error": str(exc)},
                        timestamp=datetime.now(timezone.utc),
                    )
                )

        self.logger.info("observability_validation_complete", checked=len(self.checks))
        return self.checks

    async def _check_metrics_registry(self) -> ObservabilityCheck:
        """Check Prometheus metrics registry.

        Returns:
            ObservabilityCheck object
        """
        try:
            metrics = list(REGISTRY.collect())
            return ObservabilityCheck(
                name="metrics_registry",
                status=ObservabilityStatus.HEALTHY,
                message=f"Metrics registry has {len(metrics)} metric families",
                details={"metric_count": len(metrics)},
                timestamp=datetime.now(timezone.utc),
            )
        except Exception as exc:
            return ObservabilityCheck(
                name="metrics_registry",
                status=ObservabilityStatus.UNHEALTHY,
                message=f"Metrics registry check failed: {exc}",
                details={"error": str(exc)},
                timestamp=datetime.now(timezone.utc),
            )

    async def _check_required_metrics(self) -> ObservabilityCheck:
        """Check for required metrics.

        Returns:
            ObservabilityCheck object
        """
        required_metrics = {
            "llm_request_latency_ms",
            "llm_tokens_input",
            "llm_tokens_output",
            "llm_failures",
            "llm_estimated_cost_usd",
            "recommendation_generation_time_ms",
            "retrieval_topk_latency_ms",
            "websocket_active_connections",
            "redis_stream_consumer_lag",
            "agent_execution_failures",
            "embedding_generation_duration_ms",
        }

        metric_names = {sample.name for metric in REGISTRY.collect() for sample in metric.samples}
        missing = sorted(metric for metric in required_metrics if not any(name.startswith(metric) for name in metric_names))

        if not missing:
            return ObservabilityCheck(
                name="required_metrics",
                status=ObservabilityStatus.HEALTHY,
                message="All required metrics registered",
                details={"required_count": len(required_metrics)},
                timestamp=datetime.now(timezone.utc),
            )

        return ObservabilityCheck(
            name="required_metrics",
            status=ObservabilityStatus.DEGRADED,
            message=f"Missing {len(missing)} required metrics",
            details={"missing": missing},
            timestamp=datetime.now(timezone.utc),
        )

    async def _check_logging_configured(self) -> ObservabilityCheck:
        """Check if logging is properly configured.

        Returns:
            ObservabilityCheck object
        """
        try:
            from app.logging import get_logger
            logger = get_logger(__name__)
            logger.info("logging_test", test=True)
            return ObservabilityCheck(
                name="logging",
                status=ObservabilityStatus.HEALTHY,
                message="Logging system operational",
                details={},
                timestamp=datetime.now(timezone.utc),
            )
        except Exception as exc:
            return ObservabilityCheck(
                name="logging",
                status=ObservabilityStatus.UNHEALTHY,
                message=f"Logging check failed: {exc}",
                details={"error": str(exc)},
                timestamp=datetime.now(timezone.utc),
            )

    def get_summary(self) -> dict[str, Any]:
        """Get observability validation summary.

        Returns:
            Summary dictionary
        """
        healthy = sum(1 for c in self.checks if c.status == ObservabilityStatus.HEALTHY)
        unhealthy = sum(1 for c in self.checks if c.status == ObservabilityStatus.UNHEALTHY)
        degraded = sum(1 for c in self.checks if c.status == ObservabilityStatus.DEGRADED)

        return {
            "total_checked": len(self.checks),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "degraded": degraded,
            "checks": [
                {"name": c.name, "status": c.status.value, "message": c.message}
                for c in self.checks
            ],
        }
