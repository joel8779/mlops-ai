"""Failure classifier - Classify CI failures by type and root cause."""

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class FailureType(str, Enum):
    """Classification of failure types."""

    DEPENDENCY = "dependency"
    IMPORT = "import"
    RUNTIME = "runtime"
    ENV = "env"
    DOCKER = "docker"
    SECRETS = "secrets"
    PYTEST = "pytest"
    OBSERVABILITY = "observability"
    LINT = "lint"
    TYPING = "typing"
    PERMISSIONS = "permissions"
    NETWORKING = "networking"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    """Severity of failure."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FailureClassification:
    """Result of failure classification."""

    failure_type: FailureType
    severity: Severity
    confidence: float
    root_cause: str
    suggested_fix: str
    timestamp: datetime


class FailureClassifier:
    """Classify CI failures by type and root cause."""

    # Patterns for different failure types
    PATTERNS = {
        FailureType.DEPENDENCY: [
            r"ModuleNotFoundError: No module named",
            r"pip install.*failed",
            r"npm ERR!.*not found",
            r"dependency.*not found",
            r"package.*not installed",
        ],
        FailureType.IMPORT: [
            r"ImportError: cannot import name",
            r"Module not found",
            r"No module named",
            r"circular import",
            r"relative import",
        ],
        FailureType.RUNTIME: [
            r"RuntimeError",
            r"Exception",
            r"Traceback",
            r"AssertionError",
            r"ValueError",
            r"KeyError",
        ],
        FailureType.ENV: [
            r"Environment variable.*not set",
            r"KeyError:.*env",
            r"missing.*environment",
            r"config.*not found",
        ],
        FailureType.DOCKER: [
            r"docker.*error",
            r"container.*failed",
            r"image.*not found",
            r"build.*failed",
            r"compose.*error",
        ],
        FailureType.SECRETS: [
            r"secret.*not found",
            r"authentication.*failed",
            r"unauthorized",
            r"permission denied",
            r"access denied",
        ],
        FailureType.PYTEST: [
            r"pytest.*failed",
            r"test.*error",
            r"fixture.*not found",
            r"collection.*failed",
            r"async.*event loop",
        ],
        FailureType.OBSERVABILITY: [
            r"metric.*not found",
            r"trace.*failed",
            r"prometheus.*error",
            r"telemetry.*failed",
        ],
        FailureType.LINT: [
            r"lint.*error",
            r"ruff.*error",
            r"eslint.*error",
            r"formatting.*error",
        ],
        FailureType.TYPING: [
            r"type.*error",
            r"mypy.*error",
            r"typescript.*error",
            r"Type.*not assignable",
        ],
        FailureType.PERMISSIONS: [
            r"permission denied",
            r"access denied",
            r"insufficient permissions",
            r"authorization.*failed",
        ],
        FailureType.NETWORKING: [
            r"connection.*refused",
            r"timeout",
            r"network.*unreachable",
            r"host.*not found",
        ],
    }

    def __init__(self) -> None:
        """Initialize failure classifier."""
        pass

    def classify(self, error_message: str, context: Optional[dict[str, Any]] = None) -> FailureClassification:
        """Classify a failure based on error message.

        Args:
            error_message: Error message or log output
            context: Additional context about the failure

        Returns:
            FailureClassification object
        """
        error_lower = error_message.lower()
        best_match = None
        best_confidence = 0.0

        for failure_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    confidence = self._calculate_confidence(pattern, error_message)
                    if confidence > best_confidence:
                        best_match = failure_type
                        best_confidence = confidence

        if not best_match:
            best_match = FailureType.UNKNOWN
            best_confidence = 0.0

        severity = self._determine_severity(best_match, error_message)
        root_cause = self._determine_root_cause(best_match, error_message, context)
        suggested_fix = self._suggest_fix(best_match, root_cause, context)

        return FailureClassification(
            failure_type=best_match,
            severity=severity,
            confidence=best_confidence,
            root_cause=root_cause,
            suggested_fix=suggested_fix,
            timestamp=datetime.now(timezone.utc),
        )

    def _calculate_confidence(self, pattern: str, error_message: str) -> float:
        """Calculate confidence score for a pattern match.

        Args:
            pattern: Matched pattern
            error_message: Error message

        Returns:
            Confidence score (0.0 to 1.0)
        """
        match = re.search(pattern, error_message, re.IGNORECASE)
        if not match:
            return 0.0

        # More specific patterns get higher confidence
        if len(pattern.split()) > 3:
            return 0.9
        elif len(pattern.split()) > 2:
            return 0.7
        else:
            return 0.5

    def _determine_severity(self, failure_type: FailureType, error_message: str) -> Severity:
        """Determine severity of failure.

        Args:
            failure_type: Type of failure
            error_message: Error message

        Returns:
            Severity level
        """
        critical_keywords = ["critical", "fatal", "panic", "crash"]
        high_keywords = ["error", "failed", "timeout", "denied"]

        error_lower = error_message.lower()

        if any(keyword in error_lower for keyword in critical_keywords):
            return Severity.CRITICAL
        elif any(keyword in error_lower for keyword in high_keywords):
            return Severity.HIGH
        elif failure_type in [FailureType.DEPENDENCY, FailureType.IMPORT, FailureType.DOCKER]:
            return Severity.HIGH
        else:
            return Severity.MEDIUM

    def _determine_root_cause(self, failure_type: FailureType, error_message: str, context: Optional[dict[str, Any]]) -> str:
        """Determine root cause of failure.

        Args:
            failure_type: Type of failure
            error_message: Error message
            context: Additional context

        Returns:
            Root cause description
        """
        root_causes = {
            FailureType.DEPENDENCY: "Missing or incompatible dependency",
            FailureType.IMPORT: "Import error - missing module or circular dependency",
            FailureType.RUNTIME: "Runtime error during execution",
            FailureType.ENV: "Missing or invalid environment variable",
            FailureType.DOCKER: "Docker configuration or runtime issue",
            FailureType.SECRETS: "Missing or invalid secret/authentication",
            FailureType.PYTEST: "Test configuration or fixture issue",
            FailureType.OBSERVABILITY: "Observability stack misconfiguration",
            FailureType.LINT: "Code linting violation",
            FailureType.TYPING: "Type checking error",
            FailureType.PERMISSIONS: "Insufficient permissions",
            FailureType.NETWORKING: "Network connectivity issue",
            FailureType.UNKNOWN: "Unknown failure cause",
        }

        return root_causes.get(failure_type, "Unknown cause")

    def _suggest_fix(self, failure_type: FailureType, root_cause: str, context: Optional[dict[str, Any]]) -> str:
        """Suggest fix for the failure.

        Args:
            failure_type: Type of failure
            root_cause: Root cause description
            context: Additional context

        Returns:
            Suggested fix
        """
        fixes = {
            FailureType.DEPENDENCY: "Install missing dependency or update to compatible version",
            FailureType.IMPORT: "Fix import path or add missing __init__.py file",
            FailureType.RUNTIME: "Debug runtime error and fix code logic",
            FailureType.ENV: "Set missing environment variable in .env or CI configuration",
            FailureType.DOCKER: "Fix Dockerfile or docker-compose configuration",
            FailureType.SECRETS: "Add missing secret to environment or secret manager",
            FailureType.PYTEST: "Fix test configuration or add missing fixture",
            FailureType.OBSERVABILITY: "Configure observability stack correctly",
            FailureType.LINT: "Fix linting violations",
            FailureType.TYPING: "Fix type annotations or add type stubs",
            FailureType.PERMISSIONS: "Grant required permissions or adjust resource access",
            FailureType.NETWORKING: "Fix network configuration or check service availability",
            FailureType.UNKNOWN: "Investigate logs and debug the issue",
        }

        return fixes.get(failure_type, "No specific fix suggestion available")
