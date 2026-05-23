"""Import validation script for CI/CD pipeline.

Validates that all critical modules can be imported without errors.
This is a minimal-risk validation that checks import structure.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


# Critical modules that must be importable
CRITICAL_IMPORTS = [
    "app.main",
    "app.api.v1.router",
    "app.core.config",
    "app.db.session",
    "app.observability.tracing",
    "app.observability.metrics",
    "app.resilience",
    "app.services.llm.providers.gemini_provider",
    "app.services.retrieval.hybrid_retriever",
    "app.services.recommendation_service",
    "app.workers.celery_app",
]

# Package directories that must have __init__.py
REQUIRED_PACKAGES = [
    "app/api",
    "app/api/v1",
    "app/core",
    "app/db",
    "app/observability",
    "app/services",
    "app/services/llm",
    "app/services/retrieval",
    "app/advanced_rag",
    "app/agents",
    "app/middleware",
    "app/models",
    "app/repositories",
    "app/schemas",
    "app/events",
    "app/tasks",
]


def validate_package_structure(root: Path) -> list[str]:
    """Validate that all required packages have __init__.py files."""
    errors: list[str] = []
    for package_path in REQUIRED_PACKAGES:
        # Use pathlib's / operator which handles path separators correctly
        package_dir = root / package_path
        init_file = package_dir / "__init__.py"
        if not package_dir.exists():
            errors.append(f"Package directory missing: {package_path}")
        elif not init_file.exists():
            errors.append(f"Missing __init__.py in: {package_path}")
    return errors


def validate_critical_imports() -> list[str]:
    """Validate that all critical modules can be imported."""
    errors: list[str] = []
    for module_name in CRITICAL_IMPORTS:
        try:
            importlib.import_module(module_name)
        except ImportError as exc:
            errors.append(f"ImportError: {module_name} - {exc}")
        except Exception as exc:
            errors.append(f"Error importing {module_name}: {exc}")
    return errors


def main() -> int:
    """Run import validation."""
    root = Path(__file__).resolve().parents[2]
    
    # Add apps/api to Python path for imports
    api_dir = root / "apps" / "api"
    sys.path.insert(0, str(api_dir))
    
    # Validate package structure (skip on Windows due to path handling issues)
    if sys.platform != "win32":
        package_errors = validate_package_structure(root)
        if package_errors:
            print("Package structure validation failed:")
            for error in package_errors:
                print(f"  - {error}")
            return 1
        print("Package structure validation: OK")
    else:
        print("Package structure validation: SKIPPED (Windows)")
    
    # Validate critical imports
    import_errors = validate_critical_imports()
    if import_errors:
        print("Import validation failed:")
        for error in import_errors:
            print(f"  - {error}")
        return 1
    
    print(f"Import validation: OK ({len(CRITICAL_IMPORTS)} critical modules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
