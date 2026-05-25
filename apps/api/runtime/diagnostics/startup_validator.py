"""Startup validator - Comprehensive startup diagnostics."""

import sys
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.logging import get_logger


class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    name: str
    status: HealthStatus
    message: str
    details: dict[str, Any]
    timestamp: datetime
    duration_ms: float


class StartupValidator:
    """Comprehensive startup validation."""

    def __init__(self) -> None:
        """Initialize startup validator."""
        self.logger = get_logger(__name__)
        self.results: list[ValidationResult] = []

    async def validate_all(self) -> list[ValidationResult]:
        """Run all startup validations.

        Returns:
            List of ValidationResult objects
        """
        self.logger.info("startup_validation_beginning")

        validations = [
            self._validate_python_version,
            self._validate_environment_variables,
            self._validate_imports,
        ]

        for validation in validations:
            try:
                result = await validation()
                self.results.append(result)
            except Exception as exc:
                self.logger.exception("validation_failed", validation=validation.__name__)
                self.results.append(
                    ValidationResult(
                        name=validation.__name__,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Validation failed: {exc}",
                        details={"error": str(exc)},
                        timestamp=datetime.now(timezone.utc),
                        duration_ms=0,
                    )
                )

        self.logger.info("startup_validation_complete", results=len(self.results))
        return self.results

    async def _validate_python_version(self) -> ValidationResult:
        """Validate Python version.

        Returns:
            ValidationResult
        """
        start = asyncio.get_event_loop().time()
        version = sys.version_info
        required = (3, 11)

        if version >= required:
            return ValidationResult(
                name="python_version",
                status=HealthStatus.HEALTHY,
                message=f"Python {version.major}.{version.minor}.{version.micro}",
                details={"version": f"{version.major}.{version.minor}.{version.micro}", "required": f"{required[0]}.{required[1]}"},
                timestamp=datetime.now(timezone.utc),
                duration_ms=(asyncio.get_event_loop().time() - start) * 1000,
            )

        return ValidationResult(
            name="python_version",
            status=HealthStatus.UNHEALTHY,
            message=f"Python {version.major}.{version.minor} required {required[0]}.{required[1]}+",
            details={"version": f"{version.major}.{version.minor}", "required": f"{required[0]}.{required[1]}"},
            timestamp=datetime.now(timezone.utc),
            duration_ms=(asyncio.get_event_loop().time() - start) * 1000,
        )

    async def _validate_environment_variables(self) -> ValidationResult:
        """Validate required environment variables.

        Returns:
            ValidationResult
        """
        start = asyncio.get_event_loop().time()
        required_vars = [
            "ENVIRONMENT",
            "DATABASE_URL",
            "REDIS_URL",
            "JWT_SECRET_KEY",
        ]

        missing = []
        for var in required_vars:
            if not getattr(settings, var.lower(), None):
                missing.append(var)

        if not missing:
            return ValidationResult(
                name="environment_variables",
                status=HealthStatus.HEALTHY,
                message="All required environment variables set",
                details={"checked": len(required_vars)},
                timestamp=datetime.now(timezone.utc),
                duration_ms=(asyncio.get_event_loop().time() - start) * 1000,
            )

        return ValidationResult(
            name="environment_variables",
            status=HealthStatus.UNHEALTHY,
            message=f"Missing environment variables: {', '.join(missing)}",
            details={"missing": missing},
            timestamp=datetime.now(timezone.utc),
            duration_ms=(asyncio.get_event_loop().time() - start) * 1000,
        )

    async def _validate_imports(self) -> ValidationResult:
        """Validate critical imports.

        Returns:
            ValidationResult
        """
        start = asyncio.get_event_loop().time()
        critical_imports = [
            "fastapi",
            "sqlalchemy",
            "redis",
            "celery",
            "qdrant_client",
            "google.genai",
        ]

        failed_imports = []
        for module in critical_imports:
            try:
                __import__(module)
            except ImportError as exc:
                failed_imports.append((module, str(exc)))

        if not failed_imports:
            return ValidationResult(
                name="critical_imports",
                status=HealthStatus.HEALTHY,
                message="All critical imports successful",
                details={"checked": len(critical_imports)},
                timestamp=datetime.now(timezone.utc),
                duration_ms=(asyncio.get_event_loop().time() - start) * 1000,
            )

        return ValidationResult(
            name="critical_imports",
            status=HealthStatus.UNHEALTHY,
            message=f"Failed imports: {', '.join(f[0] for f in failed_imports)}",
            details={"failed": failed_imports},
            timestamp=datetime.now(timezone.utc),
            duration_ms=(asyncio.get_event_loop().time() - start) * 1000,
        )

    def get_summary(self) -> dict[str, Any]:
        """Get validation summary.

        Returns:
            Summary dictionary
        """
        healthy = sum(1 for r in self.results if r.status == HealthStatus.HEALTHY)
        unhealthy = sum(1 for r in self.results if r.status == HealthStatus.UNHEALTHY)
        degraded = sum(1 for r in self.results if r.status == HealthStatus.DEGRADED)

        overall_status = HealthStatus.HEALTHY
        if unhealthy > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall_status = HealthStatus.DEGRADED

        return {
            "overall_status": overall_status.value,
            "total_validations": len(self.results),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "degraded": degraded,
            "results": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "message": r.message,
                    "duration_ms": r.duration_ms,
                }
                for r in self.results
            ],
        }

    def fail_fast_if_unhealthy(self) -> None:
        """Fail fast if any validation is unhealthy.

        Raises:
            SystemExit: If any validation is unhealthy
        """
        unhealthy_results = [r for r in self.results if r.status == HealthStatus.UNHEALTHY]
        if unhealthy_results:
            self.logger.error("startup_validation_failed", failures=len(unhealthy_results))
            for result in unhealthy_results:
                self.logger.error("validation_failure", name=result.name, message=result.message)
            raise SystemExit(1)
