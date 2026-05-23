"""Environment validator - Validate environment configuration."""

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from app.core.config import settings
from app.logging import get_logger


class EnvStatus(str, Enum):
    """Environment validation status."""

    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"
    INSECURE = "insecure"


@dataclass
class EnvCheck:
    """Result of an environment check."""

    name: str
    status: EnvStatus
    message: str
    value: Optional[str]
    timestamp: datetime


class EnvValidator:
    """Validate environment configuration."""

    def __init__(self) -> None:
        """Initialize environment validator."""
        self.logger = get_logger(__name__)
        self.checks: list[EnvCheck] = []

    async def validate_all(self) -> list[EnvCheck]:
        """Validate all environment variables.

        Returns:
            List of EnvCheck objects
        """
        self.logger.info("env_validation_beginning")

        required_vars = {
            "ENVIRONMENT": self._validate_environment,
            "DATABASE_URL": self._validate_database_url,
            "REDIS_URL": self._validate_redis_url,
            "JWT_SECRET_KEY": self._validate_jwt_secret,
            "LLM_PROVIDER": self._validate_llm_provider,
        }

        for var_name, validator in required_vars.items():
            check = validator(var_name)
            self.checks.append(check)

        self.logger.info("env_validation_complete", checked=len(self.checks))
        return self.checks

    def _validate_environment(self, var_name: str) -> EnvCheck:
        """Validate ENVIRONMENT variable.

        Args:
            var_name: Variable name

        Returns:
            EnvCheck object
        """
        value = os.getenv(var_name)
        valid_values = ["development", "staging", "production", "test"]

        if not value:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.MISSING,
                message="Environment variable not set",
                value=None,
                timestamp=datetime.now(timezone.utc),
            )

        if value.lower() not in valid_values:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.INVALID,
                message=f"Invalid value: {value}. Valid: {valid_values}",
                value=value,
                timestamp=datetime.now(timezone.utc),
            )

        return EnvCheck(
            name=var_name,
            status=EnvStatus.VALID,
            message=f"Environment set to {value}",
            value=value,
            timestamp=datetime.now(timezone.utc),
        )

    def _validate_database_url(self, var_name: str) -> EnvCheck:
        """Validate DATABASE_URL.

        Args:
            var_name: Variable name

        Returns:
            EnvCheck object
        """
        value = os.getenv(var_name)

        if not value:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.MISSING,
                message="Database URL not set",
                value=None,
                timestamp=datetime.now(timezone.utc),
            )

        if "postgresql" not in value and "sqlite" not in value:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.INVALID,
                message="Invalid database URL format",
                value=value[:50] + "..." if len(value) > 50 else value,
                timestamp=datetime.now(timezone.utc),
            )

        return EnvCheck(
            name=var_name,
            status=EnvStatus.VALID,
            message="Database URL format valid",
            value=value[:50] + "..." if len(value) > 50 else value,
            timestamp=datetime.now(timezone.utc),
        )

    def _validate_redis_url(self, var_name: str) -> EnvCheck:
        """Validate REDIS_URL.

        Args:
            var_name: Variable name

        Returns:
            EnvCheck object
        """
        value = os.getenv(var_name)

        if not value:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.MISSING,
                message="Redis URL not set",
                value=None,
                timestamp=datetime.now(timezone.utc),
            )

        if not value.startswith("redis://"):
            return EnvCheck(
                name=var_name,
                status=EnvStatus.INVALID,
                message="Invalid Redis URL format",
                value=value,
                timestamp=datetime.now(timezone.utc),
            )

        return EnvCheck(
            name=var_name,
            status=EnvStatus.VALID,
            message="Redis URL format valid",
            value=value,
            timestamp=datetime.now(timezone.utc),
        )

    def _validate_jwt_secret(self, var_name: str) -> EnvCheck:
        """Validate JWT_SECRET_KEY.

        Args:
            var_name: Variable name

        Returns:
            EnvCheck object
        """
        value = os.getenv(var_name)

        if not value:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.MISSING,
                message="JWT secret not set",
                value=None,
                timestamp=datetime.now(timezone.utc),
            )

        if len(value) < 32:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.INSECURE,
                message=f"JWT secret too short ({len(value)} < 32)",
                value="***" * len(value),
                timestamp=datetime.now(timezone.utc),
            )

        if value in ["secret", "password", "change-me", "test-secret"]:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.INSECURE,
                message="JWT secret is a default/insecure value",
                value="***" * len(value),
                timestamp=datetime.now(timezone.utc),
            )

        return EnvCheck(
            name=var_name,
            status=EnvStatus.VALID,
            message="JWT secret is secure",
            value="***" * len(value),
            timestamp=datetime.now(timezone.utc),
        )

    def _validate_llm_provider(self, var_name: str) -> EnvCheck:
        """Validate LLM_PROVIDER.

        Args:
            var_name: Variable name

        Returns:
            EnvCheck object
        """
        value = os.getenv(var_name, "disabled")
        valid_values = ["gemini", "openai", "disabled"]

        if value not in valid_values:
            return EnvCheck(
                name=var_name,
                status=EnvStatus.INVALID,
                message=f"Invalid LLM provider: {value}",
                value=value,
                timestamp=datetime.now(timezone.utc),
            )

        if value == "disabled":
            return EnvCheck(
                name=var_name,
                status=EnvStatus.VALID,
                message="LLM provider disabled",
                value=value,
                timestamp=datetime.now(timezone.utc),
            )

        return EnvCheck(
            name=var_name,
            status=EnvStatus.VALID,
            message=f"LLM provider set to {value}",
            value=value,
            timestamp=datetime.now(timezone.utc),
        )

    def get_summary(self) -> dict[str, Any]:
        """Get environment validation summary.

        Returns:
            Summary dictionary
        """
        valid = sum(1 for c in self.checks if c.status == EnvStatus.VALID)
        invalid = sum(1 for c in self.checks if c.status == EnvStatus.INVALID)
        missing = sum(1 for c in self.checks if c.status == EnvStatus.MISSING)
        insecure = sum(1 for c in self.checks if c.status == EnvStatus.INSECURE)

        return {
            "total_checked": len(self.checks),
            "valid": valid,
            "invalid": invalid,
            "missing": missing,
            "insecure": insecure,
            "issues": [
                {"name": c.name, "status": c.status.value, "message": c.message}
                for c in self.checks
                if c.status != EnvStatus.VALID
            ],
        }
