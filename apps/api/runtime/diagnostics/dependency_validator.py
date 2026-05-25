"""Dependency validator - Validate and check dependencies."""

import asyncio
import importlib.metadata as metadata
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from app.logging import get_logger


class DependencyStatus(str, Enum):
    """Dependency validation status."""

    INSTALLED = "installed"
    MISSING = "missing"
    VERSION_MISMATCH = "version_mismatch"
    OUTDATED = "outdated"


@dataclass
class DependencyCheck:
    """Result of a dependency check."""

    name: str
    status: DependencyStatus
    installed_version: Optional[str]
    required_version: Optional[str]
    message: str
    timestamp: datetime


class DependencyValidator:
    """Validate Python dependencies."""

    def __init__(self) -> None:
        """Initialize dependency validator."""
        self.logger = get_logger(__name__)
        self.checks: list[DependencyCheck] = []

    async def validate_all(self) -> list[DependencyCheck]:
        """Validate all critical dependencies.

        Returns:
            List of DependencyCheck objects
        """
        self.logger.info("dependency_validation_beginning")

        critical_deps = {
            "fastapi": "0.115.0",
            "uvicorn": "0.34.0",
            "sqlalchemy": "2.0.0",
            "redis": "5.0.0",
            "celery": "5.0.0",
            "qdrant-client": "1.0.0",
            "google-genai": "2.6.0",
            "protobuf": "6.31.1",
            "grpcio": "1.76.0",
            "grpcio-tools": "1.76.0",
            "grpcio-status": "1.76.0",
            "prometheus-client": "0.20.0",
            "opentelemetry-api": "1.0.0",
        }

        for name, min_version in critical_deps.items():
            check = await self._check_dependency(name, min_version)
            self.checks.append(check)

        self.logger.info("dependency_validation_complete", checked=len(self.checks))
        return self.checks

    async def _check_dependency(self, name: str, min_version: str) -> DependencyCheck:
        """Check a single dependency.

        Args:
            name: Package name
            min_version: Minimum required version

        Returns:
            DependencyCheck object
        """
        try:
            version = metadata.version(name)
            if self._version_satisfies(version, min_version):
                return DependencyCheck(
                    name=name,
                    status=DependencyStatus.INSTALLED,
                    installed_version=version,
                    required_version=min_version,
                    message=f"Installed {version} (>= {min_version})",
                    timestamp=datetime.now(timezone.utc),
                )
            else:
                return DependencyCheck(
                    name=name,
                    status=DependencyStatus.VERSION_MISMATCH,
                    installed_version=version,
                    required_version=min_version,
                    message=f"Version {version} < {min_version}",
                    timestamp=datetime.now(timezone.utc),
                )
        except metadata.PackageNotFoundError:
            return DependencyCheck(
                name=name,
                status=DependencyStatus.MISSING,
                installed_version=None,
                required_version=min_version,
                message=f"Package not installed",
                timestamp=datetime.now(timezone.utc),
            )

    def _version_satisfies(self, installed: str, required: str) -> bool:
        """Check if installed version satisfies requirement.

        Args:
            installed: Installed version string
            required: Required version string

        Returns:
            True if version satisfies requirement
        """
        try:
            from packaging import version as pkg_version
            return pkg_version.parse(installed) >= pkg_version.parse(required)
        except Exception:
            return True  # Assume OK if parsing fails

    def get_summary(self) -> dict[str, Any]:
        """Get dependency validation summary.

        Returns:
            Summary dictionary
        """
        installed = sum(1 for c in self.checks if c.status == DependencyStatus.INSTALLED)
        missing = sum(1 for c in self.checks if c.status == DependencyStatus.MISSING)
        mismatch = sum(1 for c in self.checks if c.status == DependencyStatus.VERSION_MISMATCH)

        return {
            "total_checked": len(self.checks),
            "installed": installed,
            "missing": missing,
            "version_mismatch": mismatch,
            "issues": [
                {"name": c.name, "status": c.status.value, "message": c.message}
                for c in self.checks
                if c.status != DependencyStatus.INSTALLED
            ],
        }
