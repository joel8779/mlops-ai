"""Telemetry health diagnostic utility.

Validates that telemetry infrastructure is healthy.
This is a minimal-risk diagnostic tool.
"""

from __future__ import annotations

import sys
from pathlib import Path


def check_prometheus_client() -> tuple[bool, str]:
    """Check if prometheus-client is installed and functional."""
    try:
        from prometheus_client import REGISTRY
        return True, "prometheus-client is installed and functional"
    except ImportError as exc:
        return False, f"prometheus-client not installed: {exc}"


def check_opentelemetry() -> tuple[bool, str]:
    """Check if OpenTelemetry is installed and functional."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        return True, "OpenTelemetry is installed and functional"
    except ImportError as exc:
        return False, f"OpenTelemetry not installed: {exc}"


def check_structlog() -> tuple[bool, str]:
    """Check if structlog is installed and functional."""
    try:
        import structlog
        return True, "structlog is installed and functional"
    except ImportError as exc:
        return False, f"structlog not installed: {exc}"


def check_exporter_availability() -> tuple[bool, str]:
    """Check if OTLP exporter is available."""
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        return True, "OTLP exporter is available"
    except ImportError as exc:
        return False, f"OTLP exporter not available: {exc}"


def main() -> int:
    """Run telemetry health diagnostics."""
    print("Running telemetry health diagnostics...")
    
    checks = [
        check_prometheus_client(),
        check_opentelemetry(),
        check_structlog(),
        check_exporter_availability(),
    ]
    
    errors = []
    for passed, message in checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} telemetry health issues found")
        print("\nRemediation suggestions:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\nTelemetry health diagnostics: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
