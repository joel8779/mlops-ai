"""Python runtime verification script for PHASE 20.

Validates Python version compatibility and provides developer-friendly errors.
"""
import sys
from pathlib import Path


def verify_python_version() -> tuple[bool, str]:
    """Verify Python version meets project requirements.
    
    Project requires: Python >=3.11,<3.13
    
    Returns:
        tuple: (is_valid, message)
    """
    version = sys.version_info
    major, minor = version.major, version.minor
    
    # Check minimum version
    if major < 3 or (major == 3 and minor < 11):
        return False, f"Python {major}.{minor} is too old. Required: Python >=3.11,<3.13"
    
    # Check maximum version
    if major > 3 or (major == 3 and minor >= 13):
        return False, f"Python {major}.{minor} is too new. Required: Python >=3.11,<3.13"
    
    return True, f"Python {major}.{minor} is compatible"


def verify_pyproject_toml() -> tuple[bool, str]:
    """Verify pyproject.toml exists and has correct Python requirement.
    
    Returns:
        tuple: (is_valid, message)
    """
    pyproject_path = Path("apps/api/pyproject.toml")
    
    if not pyproject_path.exists():
        return False, f"pyproject.toml not found at {pyproject_path}"
    
    content = pyproject_path.read_text()
    
    if 'requires-python = ">=3.11,<3.13"' in content:
        return True, "pyproject.toml has correct Python requirement"
    
    return False, "pyproject.toml does not have correct Python requirement (>=3.11,<3.13)"


def verify_dockerfile() -> tuple[bool, str]:
    """Verify Dockerfile uses correct Python version.
    
    Returns:
        tuple: (is_valid, message)
    """
    dockerfile_path = Path("apps/api/Dockerfile")
    
    if not dockerfile_path.exists():
        return False, f"Dockerfile not found at {dockerfile_path}"
    
    content = dockerfile_path.read_text()
    
    if "python:3.11-slim" in content:
        return True, "Dockerfile uses correct Python version (3.11-slim)"
    
    return False, "Dockerfile does not use Python 3.11-slim"


def verify_venv_python() -> tuple[bool, str]:
    """Verify .venv Python matches current Python.
    
    Returns:
        tuple: (is_valid, message)
    """
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        return False, ".venv does not exist. Run: python -m venv .venv"
    
    # Check if venv is activated
    if sys.prefix == sys.base_prefix:
        return False, ".venv is not activated. Activate it first"
    
    return True, ".venv is activated and using current Python"


def main() -> int:
    """Run all verification checks.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("Python Runtime Verification - PHASE 20")
    print("=" * 60)
    
    checks = [
        ("Python Version", verify_python_version),
        ("pyproject.toml", verify_pyproject_toml),
        ("Dockerfile", verify_dockerfile),
        (".venv", verify_venv_python),
    ]
    
    all_passed = True
    
    for name, check_fn in checks:
        print(f"\n{name}:")
        try:
            is_valid, message = check_fn()
            if is_valid:
                print(f"  ✓ {message}")
            else:
                print(f"  ✗ {message}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All checks passed")
        print("=" * 60)
        return 0
    else:
        print("✗ Some checks failed")
        print("=" * 60)
        print("\nTo fix Python version issues:")
        print("1. Install Python 3.11 or 3.12 from https://www.python.org/downloads/")
        print("2. Recreate virtual environment:")
        print("   python -m venv .venv")
        print("   .venv\\Scripts\\activate  # Windows")
        print("   source .venv/bin/activate  # Linux/Mac")
        print("3. Reinstall dependencies:")
        print("   pip install -r apps/api/requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
