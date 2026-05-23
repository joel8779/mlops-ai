"""Readiness audit diagnostic utility.

Validates that services are ready for startup.
This is a minimal-risk diagnostic tool.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def check_environment_variables() -> tuple[bool, str]:
    """Check that critical environment variables are set."""
    critical_vars = [
        "ENVIRONMENT",
        "DATABASE_URL",
        "REDIS_URL",
        "QDRANT_URL",
    ]
    
    missing = []
    for var in critical_vars:
        if var not in os.environ or not os.environ[var]:
            missing.append(var)
    
    if missing:
        return False, f"Missing environment variables: {', '.join(missing)}"
    return True, "All critical environment variables are set"


def check_database_url_format() -> tuple[bool, str]:
    """Check that DATABASE_URL has correct format."""
    database_url = os.environ.get("DATABASE_URL", "")
    
    if not database_url:
        return False, "DATABASE_URL not set"
    
    if not database_url.startswith(("postgresql://", "postgresql+asyncpg://", "postgresql+psycopg://")):
        return False, f"DATABASE_URL has invalid format: {database_url[:50]}..."
    
    return True, "DATABASE_URL format is correct"


def check_redis_url_format() -> tuple[bool, str]:
    """Check that REDIS_URL has correct format."""
    redis_url = os.environ.get("REDIS_URL", "")
    
    if not redis_url:
        return False, "REDIS_URL not set"
    
    if not redis_url.startswith("redis://"):
        return False, f"REDIS_URL has invalid format: {redis_url[:50]}..."
    
    return True, "REDIS_URL format is correct"


def check_qdrant_url_format() -> tuple[bool, str]:
    """Check that QDRANT_URL has correct format."""
    qdrant_url = os.environ.get("QDRANT_URL", "")
    
    if not qdrant_url:
        return False, "QDRANT_URL not set"
    
    if not qdrant_url.startswith(("http://", "https://")):
        return False, f"QDRANT_URL has invalid format: {qdrant_url[:50]}..."
    
    return True, "QDRANT_URL format is correct"


def check_python_version() -> tuple[bool, str]:
    """Check that Python version is supported."""
    major, minor = sys.version_info[:2]
    if (major, minor) not in [(3, 11), (3.12)]:
        return False, f"Python {major}.{minor} not supported (requires 3.11 or 3.12)"
    return True, f"Python {major}.{minor} is supported"


def main() -> int:
    """Run readiness audit diagnostics."""
    print("Running readiness audit diagnostics...")
    
    checks = [
        check_environment_variables(),
        check_database_url_format(),
        check_redis_url_format(),
        check_qdrant_url_format(),
        check_python_version(),
    ]
    
    errors = []
    for passed, message in checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} readiness audit issues found")
        print("\nRemediation suggestions:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\nReadiness audit diagnostics: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
