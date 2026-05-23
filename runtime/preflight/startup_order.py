"""Startup order validation for CI/CD preflight checks.

Validates that the application can start up in the correct order.
This is a minimal-risk validation that checks startup dependencies.
"""

from __future__ import annotations

import sys
from pathlib import Path


def validate_startup_imports() -> list[str]:
    """Validate that critical modules can be imported in startup order."""
    errors: list[str] = []
    
    # Import order should match startup dependencies
    startup_order = [
        ("app.core.config", "Configuration"),
        ("app.db.session", "Database session"),
        ("app.observability.tracing", "Tracing"),
        ("app.observability.metrics", "Metrics"),
        ("app.main", "FastAPI app"),
    ]
    
    for module_name, description in startup_order:
        try:
            __import__(module_name)
        except ImportError as exc:
            errors.append(f"{description} ({module_name}): {exc}")
        except Exception as exc:
            errors.append(f"{description} ({module_name}): {exc}")
    
    return errors


def main() -> int:
    """Run startup order validation."""
    # Add apps/api to Python path
    root = Path(__file__).resolve().parents[2]
    api_dir = root / "apps" / "api"
    sys.path.insert(0, str(api_dir))
    
    print("Validating startup import order...")
    errors = validate_startup_imports()
    
    if errors:
        print("ERROR: Startup order validation failed:")
        for error in errors:
            print(f"  - {error}")
        print("\nRemediation: Ensure all dependencies are installed via requirements-dev.txt")
        return 1
    
    print("Startup order validation: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
