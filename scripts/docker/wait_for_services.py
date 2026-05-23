"""Wait for services to be healthy - Startup dependency management."""

import asyncio
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class ServiceWaitResult:
    """Result of waiting for a service."""

    service_name: str
    healthy: bool
    duration_seconds: float
    error: Optional[str]
    timestamp: datetime


class ServiceWaiter:
    """Wait for services to become healthy."""

    def __init__(self, timeout_seconds: int = 300, poll_interval_seconds: int = 2) -> None:
        """Initialize service waiter.

        Args:
            timeout_seconds: Maximum time to wait for each service
            poll_interval_seconds: Time between health checks
        """
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.results: list[ServiceWaitResult] = []

    async def wait_for_all(self, services: list[dict[str, Any]]) -> list[ServiceWaitResult]:
        """Wait for all services to become healthy.

        Args:
            services: List of service configurations with 'name' and 'check' function

        Returns:
            List of ServiceWaitResult objects
        """
        print(f"Waiting for {len(services)} services to be healthy...")

        for service in services:
            result = await self._wait_for_service(service)
            self.results.append(result)

        return self.results

    async def _wait_for_service(self, service: dict[str, Any]) -> ServiceWaitResult:
        """Wait for a single service to become healthy.

        Args:
            service: Service configuration

        Returns:
            ServiceWaitResult
        """
        name = service["name"]
        check_func = service["check"]

        print(f"Waiting for {name}...")

        start_time = time.time()
        deadline = start_time + self.timeout_seconds

        while time.time() < deadline:
            try:
                is_healthy = await check_func()
                if is_healthy:
                    duration = time.time() - start_time
                    print(f"✓ {name} is healthy ({duration:.1f}s)")
                    return ServiceWaitResult(
                        service_name=name,
                        healthy=True,
                        duration_seconds=duration,
                        error=None,
                        timestamp=datetime.now(timezone.utc),
                    )
            except Exception as exc:
                # Check failed, continue waiting
                pass

            await asyncio.sleep(self.poll_interval_seconds)

        # Timeout
        duration = time.time() - start_time
        print(f"✗ {name} failed to become healthy within {self.timeout_seconds}s")
        return ServiceWaitResult(
            service_name=name,
            healthy=False,
            duration_seconds=duration,
            error="Timeout waiting for service to become healthy",
            timestamp=datetime.now(timezone.utc),
        )

    def get_summary(self) -> dict[str, Any]:
        """Get wait summary.

        Returns:
            Summary dictionary
        """
        healthy = sum(1 for r in self.results if r.healthy)
        unhealthy = sum(1 for r in self.results if not r.healthy)

        return {
            "total_services": len(self.results),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "results": [
                {
                    "service_name": r.service_name,
                    "healthy": r.healthy,
                    "duration_seconds": r.duration_seconds,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


async def check_database() -> bool:
    """Check if database is healthy.

    Returns:
        True if healthy
    """
    import subprocess

    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "postgres", "pg_isready"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


async def check_redis() -> bool:
    """Check if Redis is healthy.

    Returns:
        True if healthy
    """
    import subprocess

    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "redis", "redis-cli", "ping"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0 and b"PONG" in result.stdout
    except Exception:
        return False


async def check_qdrant() -> bool:
    """Check if Qdrant is healthy.

    Returns:
        True if healthy
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:6333/")
            return response.status_code == 200
    except Exception:
        return False


async def check_api() -> bool:
    """Check if API is healthy.

    Returns:
        True if healthy
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:8000/health")
            return response.status_code == 200
    except Exception:
        return False


async def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    waiter = ServiceWaiter(timeout_seconds=300, poll_interval_seconds=2)

    services = [
        {"name": "database", "check": check_database},
        {"name": "redis", "check": check_redis},
        {"name": "qdrant", "check": check_qdrant},
        {"name": "api", "check": check_api},
    ]

    await waiter.wait_for_all(services)

    summary = waiter.get_summary()
    print(json.dumps(summary, indent=2))

    # Exit with error if any services are unhealthy
    if summary["unhealthy"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    import json
    sys.exit(asyncio.run(main()))
