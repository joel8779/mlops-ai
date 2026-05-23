"""Dependency graph validation for CI/CD preflight checks.

Validates that the dependency graph is consistent and free of conflicts.
This is a minimal-risk validation that checks dependency integrity.
"""

from __future__ import annotations

import sys
from pathlib import Path


def validate_pinned_dependencies(requirements_file: Path) -> list[str]:
    """Validate that all dependencies are pinned with ==."""
    errors: list[str] = []
    
    if not requirements_file.exists():
        errors.append(f"Requirements file not found: {requirements_file}")
        return errors
    
    content = requirements_file.read_text()
    for line_num, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-r"):
            continue
        if "==" not in line:
            errors.append(f"Line {line_num}: Unpinned dependency: {line}")
    
    return errors


def validate_no_duplicate_packages(requirements_file: Path) -> list[str]:
    """Validate that there are no duplicate package specifications."""
    errors: list[str] = []
    
    if not requirements_file.exists():
        errors.append(f"Requirements file not found: {requirements_file}")
        return errors
    
    content = requirements_file.read_text()
    packages = {}
    
    for line_num, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-r"):
            continue
        
        # Extract package name (before ==)
        package_name = line.split("==")[0].strip()
        if package_name in packages:
            errors.append(f"Line {line_num}: Duplicate package {package_name} (first at line {packages[package_name]})")
        else:
            packages[package_name] = line_num
    
    return errors


def main() -> int:
    """Run dependency graph validation."""
    root = Path(__file__).resolve().parents[2]
    requirements_file = root / "apps/api/requirements.txt"
    requirements_dev_file = root / "apps/api/requirements-dev.txt"
    
    all_errors: list[str] = []
    
    # Validate pinned dependencies
    print("Validating pinned dependencies...")
    errors = validate_pinned_dependencies(requirements_file)
    if errors:
        all_errors.extend([f"requirements.txt: {e}" for e in errors])
    
    errors = validate_pinned_dependencies(requirements_dev_file)
    if errors:
        all_errors.extend([f"requirements-dev.txt: {e}" for e in errors])
    
    # Validate no duplicates
    print("Validating no duplicate packages...")
    errors = validate_no_duplicate_packages(requirements_file)
    if errors:
        all_errors.extend([f"requirements.txt: {e}" for e in errors])
    
    errors = validate_no_duplicate_packages(requirements_dev_file)
    if errors:
        all_errors.extend([f"requirements-dev.txt: {e}" for e in errors])
    
    if all_errors:
        print("ERROR: Dependency graph validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    
    print("Dependency graph validation: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
