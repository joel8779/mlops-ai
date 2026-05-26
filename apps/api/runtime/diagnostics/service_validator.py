"""Service validator - Validate external service connectivity."""

import asyncio
import httpx
from sqlalchemy import text
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.logging import get_logger


class ServiceStatus(str, Enum):
    """Service health status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ServiceCheck:
    """Result of a service health check."""

    name: str
    status: ServiceStatus
    message: str
    latency_ms: float
    timestamp: datetime
    details: dict[str, Any]


class ServiceValidator:
    """Validate external service connectivity."""

    def __init__(self) -> None:
        """Initialize service validator."""
        self.logger = get_logger(__name__)
        self.checks: list[ServiceCheck] = []
        self._http_client: Optional[httpx.AsyncClient] = None

    async def validate_all(self) -> list[ServiceCheck]:
        """Validate all external services.

        Returns:
            List of ServiceCheck objects
        """
        self.logger.info("service_validation_beginning")

        self._http_client = httpx.AsyncClient(timeout=5.0)

        validations = [
            self._check_database,
            self._check_redis,
            self._check_qdrant,
            self._check_gemini_api,
        ]

        for validation in validations:
            try:
                result = await validation()
                self.checks.append(result)
            except Exception as exc:
                self.logger.exception("service_check_failed", service=validation.__name__)
                self.checks.append(
                    ServiceCheck(
                        name=validation.__name__,
                        status=ServiceStatus.UNHEALTHY,
                        message=f"Check failed: {exc}",
                        latency_ms=0,
                        timestamp=datetime.now(timezone.utc),
                        details={"error": str(exc)},
                    )
                )

        await self._http_client.aclose()
        self.logger.info("service_validation_complete", checked=len(self.checks))
        return self.checks

    async def _check_database(self) -> ServiceCheck:
        """Check database connectivity.

        Returns:
            ServiceCheck object
        """
        start = asyncio.get_event_loop().time()
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return ServiceCheck(
                name="database",
                status=ServiceStatus.HEALTHY,
                message="Database connection successful",
                latency_ms=latency,
                timestamp=datetime.now(timezone.utc),
                details={"url": settings.database_url},
            )
        except Exception as exc:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return ServiceCheck(
                name="database",
                status=ServiceStatus.UNHEALTHY,
                message=f"Database connection failed: {exc}",
                latency_ms=latency,
                timestamp=datetime.now(timezone.utc),
                details={"error": str(exc)},
            )

    async def _check_redis(self) -> ServiceCheck:
        """Check Redis connectivity.

        Returns:
            ServiceCheck object
        """
        start = asyncio.get_event_loop().time()
        try:
            redis = Redis.from_url(settings.redis_url)
            await redis.ping()
            await redis.close()
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return ServiceCheck(
                name="redis",
                status=ServiceStatus.HEALTHY,
                message="Redis connection successful",
                latency_ms=latency,
                timestamp=datetime.now(timezone.utc),
                details={"url": settings.redis_url},
            )
        except Exception as exc:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return ServiceCheck(
                name="redis",
                status=ServiceStatus.UNHEALTHY,
                message=f"Redis connection failed: {exc}",
                latency_ms=latency,
                timestamp=datetime.now(timezone.utc),
                details={"error": str(exc)},
            )

    async def _check_qdrant(self) -> ServiceCheck:
        """Check Qdrant connectivity.

        Returns:
            ServiceCheck object
        """
        start = asyncio.get_event_loop().time()
        try:
            response = await self._http_client.get(f"{settings.qdrant_url}/")
            if response.status_code == 200:
                latency = (asyncio.get_event_loop().time() - start) * 1000
                return ServiceCheck(
                    name="qdrant",
                    status=ServiceStatus.HEALTHY,
                    message="Qdrant connection successful",
                    latency_ms=latency,
                    timestamp=datetime.now(timezone.utc),
                    details={"url": settings.qdrant_url},
                )
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return ServiceCheck(
                name="qdrant",
                status=ServiceStatus.UNHEALTHY,
                message=f"Qdrant returned status {response.status_code}",
                latency_ms=latency,
                timestamp=datetime.now(timezone.utc),
                details={"status_code": response.status_code},
            )
        except Exception as exc:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return ServiceCheck(
                name="qdrant",
                status=ServiceStatus.UNHEALTHY,
                message=f"Qdrant connection failed: {exc}",
                latency_ms=latency,
                timestamp=datetime.now(timezone.utc),
                details={"error": str(exc)},
            )

    async def _check_gemini_api(self) -> ServiceCheck:
        """Check Gemini API connectivity.

        Returns:
            ServiceCheck object
        """
        start = asyncio.get_event_loop().time()
        try:
            if settings.llm_provider == "disabled":
                return ServiceCheck(
                    name="gemini_api",
                    status=ServiceStatus.DEGRADED,
                    message="LLM provider disabled",
                    latency_ms=0,
                    timestamp=datetime.now(timezone.utc),
                    details={"provider": settings.llm_provider},
                )

            response = await self._http_client.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                params={"key": settings.gemini_api_key},
            )
            if response.status_code == 200:
                latency = (asyncio.get_event_loop().time() - start) * 1000
                return ServiceCheck(
                    name="gemini_api",
                    status=ServiceStatus.HEALTHY,
                    message="Gemini API connection successful",
                    latency_ms=latency,
                    timestamp=datetime.now(timezone.utc),
                    details={"model": settings.gemini_model},
                )
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return ServiceCheck(
                name="gemini_api",
                status=ServiceStatus.UNHEALTHY,
                message=f"Gemini API returned status {response.status_code}",
                latency_ms=latency,
                timestamp=datetime.now(timezone.utc),
                details={"status_code": response.status_code},
            )
        except Exception as exc:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return ServiceCheck(
                name="gemini_api",
                status=ServiceStatus.UNHEALTHY,
                message=f"Gemini API connection failed: {exc}",
                latency_ms=latency,
                timestamp=datetime.now(timezone.utc),
                details={"error": str(exc)},
            )

    def get_summary(self) -> dict[str, Any]:
        """Get service validation summary.

        Returns:
            Summary dictionary
        """
        healthy = sum(1 for c in self.checks if c.status == ServiceStatus.HEALTHY)
        unhealthy = sum(1 for c in self.checks if c.status == ServiceStatus.UNHEALTHY)
        degraded = sum(1 for c in self.checks if c.status == ServiceStatus.DEGRADED)

        return {
            "total_checked": len(self.checks),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "degraded": degraded,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "latency_ms": c.latency_ms,
                }
                for c in self.checks
            ],
        }
