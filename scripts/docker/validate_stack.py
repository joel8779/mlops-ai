"""Docker stack validation - Validate Docker Compose configuration."""

import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class ContainerStatus(str, Enum):
    """Container health status."""

    RUNNING = "running"
    STOPPED = "stopped"
    UNHEALTHY = "unhealthy"
    MISSING = "missing"


@dataclass
class ContainerCheck:
    """Result of a container check."""

    name: str
    status: ContainerStatus
    health: Optional[str]
    uptime_seconds: Optional[float]
    error: Optional[str]
    timestamp: datetime


class DockerStackValidator:
    """Validate Docker Compose stack."""

    def __init__(self, compose_file: str = "docker-compose.yml") -> None:
        """Initialize Docker stack validator.

        Args:
            compose_file: Path to docker-compose file
        """
        self.compose_file = compose_file
        self.checks: list[ContainerCheck] = []

    async def validate_all(self) -> list[ContainerCheck]:
        """Validate all containers in the stack.

        Returns:
            List of ContainerCheck objects
        """
        print(f"Validating Docker stack: {self.compose_file}")

        # Validate compose file syntax
        await self._validate_compose_syntax()

        # Get container status
        await self._check_containers()

        return self.checks

    async def _validate_compose_syntax(self) -> None:
        """Validate Docker Compose file syntax."""
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", self.compose_file, "config", "--quiet"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print(f"ERROR: Compose file validation failed: {result.stderr}")
                self.checks.append(
                    ContainerCheck(
                        name="compose_syntax",
                        status=ContainerStatus.UNHEALTHY,
                        health=None,
                        uptime_seconds=None,
                        error=result.stderr,
                        timestamp=datetime.now(timezone.utc),
                    )
                )
            else:
                print("✓ Compose file syntax valid")
        except subprocess.TimeoutExpired:
            print("ERROR: Compose validation timed out")
        except FileNotFoundError:
            print("ERROR: Docker Compose not found")

    async def _check_containers(self) -> None:
        """Check status of all containers."""
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", self.compose_file, "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print(f"ERROR: Failed to get container status: {result.stderr}")
                return

            containers = json.loads(result.stdout)

            for container in containers:
                check = self._parse_container(container)
                self.checks.append(check)

        except subprocess.TimeoutExpired:
            print("ERROR: Container status check timed out")
        except json.JSONDecodeError as exc:
            print(f"ERROR: Failed to parse container status: {exc}")
        except FileNotFoundError:
            print("ERROR: Docker not found")

    def _parse_container(self, container: dict[str, Any]) -> ContainerCheck:
        """Parse container status.

        Args:
            container: Container data from docker compose ps

        Returns:
            ContainerCheck object
        """
        name = container.get("Name", "unknown")
        state = container.get("State", "unknown")
        health = container.get("Health", None)

        status = ContainerStatus.RUNNING
        if state == "running":
            if health == "unhealthy":
                status = ContainerStatus.UNHEALTHY
        elif state == "exited" or state == "stopped":
            status = ContainerStatus.STOPPED
        else:
            status = ContainerStatus.MISSING

        uptime = None
        if status == ContainerStatus.RUNNING:
            try:
                uptime_str = container.get("Status", "")
                # Parse uptime string (e.g., "Up 2 hours")
                uptime = self._parse_uptime(uptime_str)
            except Exception:
                pass

        return ContainerCheck(
            name=name,
            status=status,
            health=health,
            uptime_seconds=uptime,
            error=None,
            timestamp=datetime.now(timezone.utc),
        )

    def _parse_uptime(self, uptime_str: str) -> Optional[float]:
        """Parse uptime string to seconds.

        Args:
            uptime_str: Uptime string (e.g., "Up 2 hours")

        Returns:
            Uptime in seconds or None
        """
        # Simple parsing - can be enhanced
        if "seconds" in uptime_str:
            try:
                return float(uptime_str.split()[1])
            except (ValueError, IndexError):
                pass
        elif "minutes" in uptime_str:
            try:
                return float(uptime_str.split()[1]) * 60
            except (ValueError, IndexError):
                pass
        elif "hours" in uptime_str:
            try:
                return float(uptime_str.split()[1]) * 3600
            except (ValueError, IndexError):
                pass
        return None

    def get_summary(self) -> dict[str, Any]:
        """Get validation summary.

        Returns:
            Summary dictionary
        """
        running = sum(1 for c in self.checks if c.status == ContainerStatus.RUNNING)
        stopped = sum(1 for c in self.checks if c.status == ContainerStatus.STOPPED)
        unhealthy = sum(1 for c in self.checks if c.status == ContainerStatus.UNHEALTHY)
        missing = sum(1 for c in self.checks if c.status == ContainerStatus.MISSING)

        return {
            "total_checked": len(self.checks),
            "running": running,
            "stopped": stopped,
            "unhealthy": unhealthy,
            "missing": missing,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "health": c.health,
                    "uptime_seconds": c.uptime_seconds,
                }
                for c in self.checks
            ],
        }


async def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    compose_file = sys.argv[1] if len(sys.argv) > 1 else "docker-compose.yml"

    validator = DockerStackValidator(compose_file)
    await validator.validate_all()

    summary = validator.get_summary()
    print(json.dumps(summary, indent=2))

    # Exit with error if any containers are unhealthy or missing
    if summary["unhealthy"] > 0 or summary["missing"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
