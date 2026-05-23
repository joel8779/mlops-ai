"""Capability validation for CI/CD preflight checks.

Validates that required runtime capabilities are available.
This is a minimal-risk validation that checks system capabilities.
"""

from __future__ import annotations

import sys
from pathlib import Path


def check_python_version() -> tuple[bool, str]:
    """Check if Python version is supported."""
    major, minor = sys.version_info[:2]
    if (major, minor) not in [(3, 11), (3, 12)]:
        return False, f"Python {major}.{minor} not supported (requires 3.11 or 3.12)"
    return True, f"Python {major}.{minor}"


def check_filesystem_permissions() -> tuple[bool, str]:
    """Check if filesystem permissions are adequate."""
    root = Path(__file__).resolve().parents[2]
    
    # Check write permissions
    test_file = root / ".preflight_test"
    try:
        test_file.touch()
        test_file.unlink()
        return True, "Filesystem permissions OK"
    except Exception as exc:
        return False, f"Filesystem permission error: {exc}"


def check_environment_variables() -> tuple[bool, str]:
    """Check if critical environment variables are set."""
    critical_vars = [
        "ENVIRONMENT",
        "DATABASE_URL",
        "REDIS_URL",
    ]
    
    missing = []
    for var in critical_vars:
        if var not in sys.environ or not sys.environ[var]:
            missing.append(var)
    
    if missing:
        return False, f"Missing environment variables: {', '.join(missing)}"
    return True, "Environment variables OK"


def main() -> int:
    """Run capability validation."""
    print("Validating runtime capabilities...")
    
    all_checks = [
        check_python_version(),
        check_filesystem_permissions(),
        check_environment_variables(),
    ]
    
    errors = []
    for passed, message in all_checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} capability checks failed")
        return 1
    
    print("\nCapability validation: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
