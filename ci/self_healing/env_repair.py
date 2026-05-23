"""Environment repair utility for CI/CD self-healing.

Identifies and suggests remediation for environment configuration issues.
This is a minimal-risk diagnostic tool.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def check_env_file_exists() -> tuple[bool, str]:
    """Check if .env file exists."""
    root = Path(__file__).resolve().parents[2]
    env_file = root / ".env"
    
    if env_file.exists():
        return True, f".env file exists at {env_file}"
    return False, ".env file not found. Create .env file with required environment variables"


def check_critical_env_vars() -> tuple[bool, str]:
    """Check if critical environment variables are set."""
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
    """Check if DATABASE_URL has correct format."""
    database_url = os.environ.get("DATABASE_URL", "")
    
    if not database_url:
        return False, "DATABASE_URL not set"
    
    if not database_url.startswith(("postgresql://", "postgresql+asyncpg://", "postgresql+psycopg://")):
        return False, f"DATABASE_URL has invalid format: {database_url[:50]}..."
    
    return True, "DATABASE_URL format is correct"


def main() -> int:
    """Run environment repair diagnostics."""
    print("Running environment repair diagnostics...")
    
    checks = [
        check_env_file_exists(),
        check_critical_env_vars(),
        check_database_url_format(),
    ]
    
    errors = []
    for passed, message in checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} environment issues found")
        print("\nRemediation suggestions:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\nEnvironment repair diagnostics: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
