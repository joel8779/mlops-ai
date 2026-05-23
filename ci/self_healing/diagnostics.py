"""CI diagnostics utility for identifying common failure patterns.

Identifies common CI failures and suggests remediation.
This is a minimal-risk diagnostic tool.
"""

from __future__ import annotations

import sys
from pathlib import Path


def check_python_version() -> tuple[bool, str]:
    """Check if Python version is supported."""
    major, minor = sys.version_info[:2]
    if (major, minor) not in [(3, 11), (3, 12)]:
        return False, f"Python {major}.{minor} not supported (requires 3.11 or 3.12)"
    return True, f"Python {major}.{minor} is supported"


def check_package_init_files() -> tuple[bool, str]:
    """Check if critical package directories have __init__.py files."""
    root = Path(__file__).resolve().parents[2]
    api_dir = root / "apps/api/app"
    
    critical_packages = [
        "api",
        "api/v1",
        "core",
        "db",
        "observability",
        "services",
    ]
    
    missing = []
    for package in critical_packages:
        package_dir = api_dir / package
        init_file = package_dir / "__init__.py"
        if not init_file.exists():
            missing.append(package)
    
    if missing:
        return False, f"Missing __init__.py files in: {', '.join(missing)}"
    return True, "All critical package directories have __init__.py files"


def check_verification_scripts() -> tuple[bool, str]:
    """Check if verification scripts exist."""
    root = Path(__file__).resolve().parents[2]
    scripts_dir = root / "scripts/ci"
    
    critical_scripts = [
        "verify_runtime.py",
        "verify_routes.py",
        "verify_observability.py",
        "verify_workers.py",
    ]
    
    missing = []
    for script in critical_scripts:
        script_file = scripts_dir / script
        if not script_file.exists():
            missing.append(script)
    
    if missing:
        return False, f"Missing verification scripts: {', '.join(missing)}"
    return True, "All verification scripts exist"


def main() -> int:
    """Run CI diagnostics."""
    print("Running CI diagnostics...")
    
    checks = [
        check_python_version(),
        check_package_init_files(),
        check_verification_scripts(),
    ]
    
    errors = []
    for passed, message in checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} diagnostic issues found")
        print("\nRemediation suggestions:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\nCI diagnostics: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
