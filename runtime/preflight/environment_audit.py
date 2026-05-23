"""Environment audit for CI/CD preflight checks.

Validates that the environment is correctly configured.
This is a minimal-risk validation that checks environment configuration.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def validate_environment_file() -> tuple[bool, str]:
    """Validate that .env file exists and is readable."""
    root = Path(__file__).resolve().parents[2]
    env_file = root / ".env"
    
    if not env_file.exists():
        return False, f".env file not found at {env_file}"
    
    try:
        content = env_file.read_text()
        if not content.strip():
            return False, ".env file is empty"
        return True, f".env file OK ({len(content.splitlines())} lines)"
    except Exception as exc:
        return False, f"Failed to read .env file: {exc}"


def validate_database_url_format() -> tuple[bool, str]:
    """Validate that DATABASE_URL has correct format."""
    database_url = os.environ.get("DATABASE_URL", "")
    
    if not database_url:
        return False, "DATABASE_URL not set"
    
    if not database_url.startswith(("postgresql://", "postgresql+asyncpg://", "postgresql+psycopg://")):
        return False, f"DATABASE_URL has invalid format: {database_url[:50]}..."
    
    return True, "DATABASE_URL format OK"


def validate_redis_url_format() -> tuple[bool, str]:
    """Validate that REDIS_URL has correct format."""
    redis_url = os.environ.get("REDIS_URL", "")
    
    if not redis_url:
        return False, "REDIS_URL not set"
    
    if not redis_url.startswith("redis://"):
        return False, f"REDIS_URL has invalid format: {redis_url[:50]}..."
    
    return True, "REDIS_URL format OK"


def validate_qdrant_url_format() -> tuple[bool, str]:
    """Validate that QDRANT_URL has correct format."""
    qdrant_url = os.environ.get("QDRANT_URL", "")
    
    if not qdrant_url:
        return False, "QDRANT_URL not set"
    
    if not qdrant_url.startswith(("http://", "https://")):
        return False, f"QDRANT_URL has invalid format: {qdrant_url[:50]}..."
    
    return True, "QDRANT_URL format OK"


def main() -> int:
    """Run environment audit."""
    print("Auditing environment configuration...")
    
    all_checks = [
        validate_environment_file(),
        validate_database_url_format(),
        validate_redis_url_format(),
        validate_qdrant_url_format(),
    ]
    
    errors = []
    for passed, message in all_checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} environment audit checks failed")
        print("\nRemediation: Ensure .env file exists with correct configuration")
        return 1
    
    print("\nEnvironment audit: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
