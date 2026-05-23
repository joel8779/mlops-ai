"""Dependency repair utility for CI/CD self-healing.

Identifies and suggests remediation for common dependency issues.
This is a minimal-risk diagnostic tool.
"""

from __future__ import annotations

import sys
from pathlib import Path


def check_torch_compatibility(requirements_file: Path) -> tuple[bool, str]:
    """Check if torch version is compatible with Python 3.11/3.12."""
    if not requirements_file.exists():
        return False, "Requirements file not found"
    
    content = requirements_file.read_text()
    for line in content.splitlines():
        if line.strip().startswith("torch=="):
            version = line.split("==")[1].strip()
            # torch 2.6.0 may not be available for Python 3.11/3.12
            if version == "2.6.0":
                return False, f"torch {version} may not be compatible with Python 3.11/3.12. Revert to 2.5.1"
            if version == "2.5.1":
                return True, f"torch {version} is compatible with Python 3.11/3.12"
    
    return False, "torch not found in requirements"


def check_opentelemetry_versions(requirements_file: Path) -> tuple[bool, str]:
    """Check if OpenTelemetry versions are aligned."""
    if not requirements_file.exists():
        return False, "Requirements file not found"
    
    content = requirements_file.read_text()
    core_version = None
    instrumentation_versions = []
    
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("opentelemetry-api=="):
            core_version = line.split("==")[1].strip()
        elif line.startswith("opentelemetry-instrumentation-"):
            version = line.split("==")[1].strip()
            instrumentation_versions.append(version)
    
    if not core_version:
        return False, "OpenTelemetry core version not found"
    
    # Check if all instrumentation versions are the same
    if len(set(instrumentation_versions)) == 1:
        return True, f"OpenTelemetry versions aligned (core: {core_version}, instrumentation: {instrumentation_versions[0]})"
    
    return False, f"OpenTelemetry instrumentation versions not aligned: {instrumentation_versions}"


def main() -> int:
    """Run dependency repair diagnostics."""
    root = Path(__file__).resolve().parents[2]
    requirements_file = root / "apps/api/requirements.txt"
    
    print("Running dependency repair diagnostics...")
    
    checks = [
        check_torch_compatibility(requirements_file),
        check_opentelemetry_versions(requirements_file),
    ]
    
    errors = []
    for passed, message in checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} dependency issues found")
        print("\nRemediation suggestions:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\nDependency repair diagnostics: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
