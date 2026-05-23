"""Remediation engine for CI/CD self-healing.

Provides automated remediation suggestions for common CI failures.
This is a minimal-risk diagnostic tool.
"""

from __future__ import annotations

import sys
from pathlib import Path


def analyze_import_errors(error_message: str) -> str:
    """Analyze import errors and suggest remediation."""
    if "torch" in error_message.lower():
        return "Torch import error: Ensure torch==2.5.1 is installed via requirements.txt"
    if "prometheus_client" in error_message.lower():
        return "Prometheus client import error: Ensure prometheus-client is installed via requirements.txt"
    if "celery" in error_message.lower():
        return "Celery import error: Ensure celery[redis] is installed via requirements.txt"
    if "opentelemetry" in error_message.lower():
        return "OpenTelemetry import error: Ensure all OTel packages are installed via requirements.txt"
    if "fastapi" in error_message.lower():
        return "FastAPI import error: Ensure fastapi and uvicorn are installed via requirements.txt"
    return f"Generic import error: {error_message}"


def analyze_dependency_errors(error_message: str) -> str:
    """Analyze dependency errors and suggest remediation."""
    if "No matching distribution" in error_message:
        return "Package not found: Check package name and version in requirements.txt"
    if "Could not find a version" in error_message:
        return "Version conflict: Check if package version exists for Python 3.11/3.12"
    if "requires a different Python" in error_message:
        return "Python version incompatibility: Ensure Python 3.11 or 3.12 is used"
    return f"Generic dependency error: {error_message}"


def analyze_docker_errors(error_message: str) -> str:
    """Analyze Docker build errors and suggest remediation."""
    if "COPY failed" in error_message:
        return "Docker COPY failed: Check if source files exist in build context"
    if "no such file or directory" in error_message:
        return "File not found: Check Dockerfile COPY/ADD paths"
    if "command not found" in error_message:
        return "Command not found: Check if dependencies are installed in Docker image"
    return f"Generic Docker error: {error_message}"


def classify_failure(error_message: str) -> str:
    """Classify failure type based on error message."""
    if "ImportError" in error_message or "ModuleNotFoundError" in error_message:
        return "IMPORT"
    if "Dependency" in error_message or "pip" in error_message.lower():
        return "DEPENDENCY"
    if "Docker" in error_message or "docker" in error_message.lower():
        return "DOCKER"
    if "Environment" in error_message or "env" in error_message.lower():
        return "ENVIRONMENT"
    return "UNKNOWN"


def suggest_remediation(error_message: str) -> str:
    """Suggest remediation based on error message."""
    failure_type = classify_failure(error_message)
    
    if failure_type == "IMPORT":
        return analyze_import_errors(error_message)
    elif failure_type == "DEPENDENCY":
        return analyze_dependency_errors(error_message)
    elif failure_type == "DOCKER":
        return analyze_docker_errors(error_message)
    elif failure_type == "ENVIRONMENT":
        return "Environment error: Check .env file and environment variables"
    else:
        return f"Unknown error type: {error_message}"


def main() -> int:
    """Run remediation engine."""
    print("Remediation Engine for CI/CD")
    print("=" * 50)
    print("\nUsage: python remediation_engine.py <error_message>")
    print("\nExample:")
    print("  python remediation_engine.py 'ImportError: No module named torch'")
    print("\nCommon failure patterns:")
    print("  - ImportError: Missing dependency")
    print("  - Dependency errors: Version conflicts")
    print("  - Docker errors: Build context issues")
    print("  - Environment errors: Missing .env or variables")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        error_message = " ".join(sys.argv[1:])
        print(f"Analyzing error: {error_message}")
        print(f"\nClassification: {classify_failure(error_message)}")
        print(f"\nRemediation: {suggest_remediation(error_message)}")
    else:
        sys.exit(main())
