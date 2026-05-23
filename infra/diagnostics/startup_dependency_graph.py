"""Startup dependency graph diagnostic utility.

Validates that startup dependencies are correctly ordered.
This is a minimal-risk diagnostic tool.
"""

from __future__ import annotations

import sys
from pathlib import Path


def check_startup_import_order() -> tuple[bool, str]:
    """Check that startup imports can be loaded in correct order."""
    root = Path(__file__).resolve().parents[2]
    api_dir = root / "apps/api"
    sys.path.insert(0, str(api_dir))
    
    startup_order = [
        ("app.core.config", "Configuration"),
        ("app.logging", "Logging"),
        ("app.observability.tracing", "Tracing"),
        ("app.db.session", "Database session"),
        ("app.main", "FastAPI app"),
    ]
    
    errors = []
    for module_name, description in startup_order:
        try:
            __import__(module_name)
        except ImportError as exc:
            errors.append(f"{description} ({module_name}): {exc}")
        except Exception as exc:
            errors.append(f"{description} ({module_name}): {exc}")
    
    if errors:
        return False, f"Startup import order failed: {', '.join(errors)}"
    return True, "Startup import order is correct"


def check_no_circular_imports() -> tuple[bool, str]:
    """Check for circular imports in critical modules."""
    root = Path(__file__).resolve().parents[2]
    api_dir = root / "apps/api"
    sys.path.insert(0, str(api_dir))
    
    critical_modules = [
        "app.main",
        "app.api.v1.router",
        "app.core.config",
        "app.observability.tracing",
    ]
    
    errors = []
    for module_name in critical_modules:
        try:
            module = __import__(module_name, fromlist=["__all__"])
            # If we get here, no circular import
        except ImportError as exc:
            if "circular" in str(exc).lower():
                errors.append(f"{module_name}: Circular import detected")
            else:
                errors.append(f"{module_name}: {exc}")
        except Exception as exc:
            errors.append(f"{module_name}: {exc}")
    
    if errors:
        return False, f"Circular import check failed: {', '.join(errors)}"
    return True, "No circular imports detected"


def check_dependency_resolution() -> tuple[bool, str]:
    """Check that dependencies can be resolved."""
    root = Path(__file__).resolve().parents[2]
    requirements_file = root / "apps/api/requirements.txt"
    
    if not requirements_file.exists():
        return False, "requirements.txt not found"
    
    content = requirements_file.read_text()
    lines = content.splitlines()
    
    # Check that all dependencies are pinned
    unpinned = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-r"):
            if "==" not in line:
                unpinned.append(line)
    
    if unpinned:
        return False, f"Unpinned dependencies: {', '.join(unpinned)}"
    return True, "All dependencies are pinned"


def main() -> int:
    """Run startup dependency graph diagnostics."""
    print("Running startup dependency graph diagnostics...")
    
    checks = [
        check_startup_import_order(),
        check_no_circular_imports(),
        check_dependency_resolution(),
    ]
    
    errors = []
    for passed, message in checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} startup dependency graph issues found")
        print("\nRemediation suggestions:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\nStartup dependency graph diagnostics: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
