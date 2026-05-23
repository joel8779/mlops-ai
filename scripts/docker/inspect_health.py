"""Docker health inspection - Detailed health check for containers."""

import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class HealthCheck:
    """Result of a health check."""

    container_name: str
    status: str
    health_status: Optional[str]
    restart_count: int
    cpu_percent: Optional[float]
    memory_usage_mb: Optional[float]
    network_rx_bytes: Optional[int]
    network_tx_bytes: Optional[int]
    error: Optional[str]
    timestamp: datetime


class DockerHealthInspector:
    """Inspect Docker container health."""

    async def inspect_all(self, compose_file: str = "docker-compose.yml") -> list[HealthCheck]:
        """Inspect health of all containers in compose stack.

        Args:
            compose_file: Path to docker-compose file

        Returns:
            List of HealthCheck objects
        """
        print(f"Inspecting Docker health for: {compose_file}")

        # Get container IDs
        container_ids = await self._get_container_ids(compose_file)

        health_checks = []
        for container_id in container_ids:
            check = await self._inspect_container(container_id)
            health_checks.append(check)

        return health_checks

    async def _get_container_ids(self, compose_file: str) -> list[str]:
        """Get container IDs from compose stack.

        Args:
            compose_file: Path to docker-compose file

        Returns:
            List of container IDs
        """
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", compose_file, "ps", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print(f"ERROR: Failed to get container IDs: {result.stderr}")
                return []

            return [cid.strip() for cid in result.stdout.strip().split("\n") if cid.strip()]

        except subprocess.TimeoutExpired:
            print("ERROR: Container ID lookup timed out")
            return []
        except FileNotFoundError:
            print("ERROR: Docker not found")
            return []

    async def _inspect_container(self, container_id: str) -> HealthCheck:
        """Inspect a single container.

        Args:
            container_id: Container ID

        Returns:
            HealthCheck object
        """
        try:
            result = subprocess.run(
                ["docker", "inspect", container_id],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return HealthCheck(
                    container_name=container_id[:12],
                    status="unknown",
                    health_status=None,
                    restart_count=0,
                    cpu_percent=None,
                    memory_usage_mb=None,
                    network_rx_bytes=None,
                    network_tx_bytes=None,
                    error=result.stderr,
                    timestamp=datetime.now(timezone.utc),
                )

            data = json.loads(result.stdout)[0]
            name = data["Name"].lstrip("/")
            state = data["State"]
            health = state.get("Health", {})

            # Get stats
            stats = await self._get_stats(container_id)

            return HealthCheck(
                container_name=name,
                status=state["Status"],
                health_status=health.get("Status"),
                restart_count=state.get("RestartCount", 0),
                cpu_percent=stats.get("cpu_percent"),
                memory_usage_mb=stats.get("memory_usage_mb"),
                network_rx_bytes=stats.get("network_rx_bytes"),
                network_tx_bytes=stats.get("network_tx_bytes"),
                error=None,
                timestamp=datetime.now(timezone.utc),
            )

        except subprocess.TimeoutExpired:
            return HealthCheck(
                container_name=container_id[:12],
                status="timeout",
                health_status=None,
                restart_count=0,
                cpu_percent=None,
                memory_usage_mb=None,
                network_rx_bytes=None,
                network_tx_bytes=None,
                error="Inspection timed out",
                timestamp=datetime.now(timezone.utc),
            )
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            return HealthCheck(
                container_name=container_id[:12],
                status="error",
                health_status=None,
                restart_count=0,
                cpu_percent=None,
                memory_usage_mb=None,
                network_rx_bytes=None,
                network_tx_bytes=None,
                error=str(exc),
                timestamp=datetime.now(timezone.utc),
            )

    async def _get_stats(self, container_id: str) -> dict[str, Any]:
        """Get container stats.

        Args:
            container_id: Container ID

        Returns:
            Stats dictionary
        """
        try:
            result = subprocess.run(
                ["docker", "stats", container_id, "--no-stream", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return {}

            data = json.loads(result.stdout)[0]

            # Parse CPU
            cpu_percent = data.get("CPUPerc")
            if cpu_percent:
                cpu_percent = float(cpu_percent.rstrip("%"))

            # Parse memory
            memory_usage_mb = None
            memory_usage = data.get("MemUsage")
            if memory_usage:
                parts = memory_usage.split("/")
                if parts:
                    mem_str = parts[0].strip()
                    if mem_str.endswith("MiB"):
                        memory_usage_mb = float(mem_str.replace("MiB", ""))
                    elif mem_str.endswith("GiB"):
                        memory_usage_mb = float(mem_str.replace("GiB", "")) * 1024

            # Parse network
            net_rx = data.get("NetIO")
            net_tx = None
            if net_rx:
                parts = net_rx.split("/")
                if parts:
                    rx_str = parts[0].strip()
                    tx_str = parts[1].strip() if len(parts) > 1 else "0B"
                    net_rx_bytes = self._parse_bytes(rx_str)
                    net_tx_bytes = self._parse_bytes(tx_str)
                else:
                    net_rx_bytes = None
                    net_tx_bytes = None
            else:
                net_rx_bytes = None
                net_tx_bytes = None

            return {
                "cpu_percent": cpu_percent,
                "memory_usage_mb": memory_usage_mb,
                "network_rx_bytes": net_rx_bytes,
                "network_tx_bytes": net_tx_bytes,
            }

        except Exception:
            return {}

    def _parse_bytes(self, byte_str: str) -> Optional[int]:
        """Parse byte string to integer.

        Args:
            byte_str: String like "1.2GiB" or "500MiB"

        Returns:
            Bytes as integer or None
        """
        try:
            byte_str = byte_str.strip().upper()
            if byte_str.endswith("B"):
                byte_str = byte_str[:-1]

            multipliers = {
                "K": 1024,
                "M": 1024 ** 2,
                "G": 1024 ** 3,
                "T": 1024 ** 4,
            }

            for suffix, mult in multipliers.items():
                if byte_str.endswith(suffix):
                    value = float(byte_str[:-1])
                    return int(value * mult)

            return int(float(byte_str))

        except (ValueError, AttributeError):
            return None

    def get_summary(self, health_checks: list[HealthCheck]) -> dict[str, Any]:
        """Get health check summary.

        Args:
            health_checks: List of HealthCheck objects

        Returns:
            Summary dictionary
        """
        healthy = sum(1 for h in health_checks if h.health_status == "healthy")
        unhealthy = sum(1 for h in health_checks if h.health_status == "unhealthy")
        starting = sum(1 for h in health_checks if h.status == "starting")

        total_cpu = sum(h.cpu_percent for h in health_checks if h.cpu_percent is not None)
        total_memory = sum(h.memory_usage_mb for h in health_checks if h.memory_usage_mb is not None)

        return {
            "total_containers": len(health_checks),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "starting": starting,
            "total_cpu_percent": round(total_cpu, 2),
            "total_memory_mb": round(total_memory, 2),
            "checks": [
                {
                    "container_name": h.container_name,
                    "status": h.status,
                    "health_status": h.health_status,
                    "restart_count": h.restart_count,
                    "cpu_percent": h.cpu_percent,
                    "memory_usage_mb": h.memory_usage_mb,
                }
                for h in health_checks
            ],
        }


async def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    compose_file = sys.argv[1] if len(sys.argv) > 1 else "docker-compose.yml"

    inspector = DockerHealthInspector()
    health_checks = await inspector.inspect_all(compose_file)

    summary = inspector.get_summary(health_checks)
    print(json.dumps(summary, indent=2))

    # Exit with error if any containers are unhealthy
    if summary["unhealthy"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
