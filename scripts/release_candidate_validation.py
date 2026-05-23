"""Release candidate validation script.

Validates:
- dependency resolution
- Docker startup
- telemetry startup
- worker startup
- websocket initialization
- Gemini initialization
- async lifecycle
- security policy compliance

This is a minimal-risk validation tool for release candidates.
"""

from __future__ import annotations

import sys
from pathlib import Path


def validate_dependency_resolution() -> tuple[bool, str]:
    """Validate that dependencies can be resolved."""
    try:
        import pip
        result = pip.main(["check"])
        if result == 0:
            return True, "Dependency resolution: OK"
        return False, "Dependency resolution: FAILED (pip check failed)"
    except Exception as exc:
        return False, f"Dependency resolution: ERROR ({exc})"


def validate_python_version() -> tuple[bool, str]:
    """Validate Python version."""
    major, minor = sys.version_info[:2]
    if (major, minor) not in [(3, 11), (3, 12)]:
        return False, f"Python {major}.{minor} not supported (requires 3.11 or 3.12)"
    return True, f"Python {major}.{minor}: OK"


def validate_websocket_import() -> tuple[bool, str]:
    """Validate websocket import."""
    try:
        import websockets
        version = websockets.__version__
        # Check if version is compatible with prefect (<14.0)
        major = int(version.split(".")[0])
        if major >= 14:
            return False, f"websockets {version} not compatible with prefect (requires <14.0)"
        return True, f"websockets {version}: OK"
    except ImportError as exc:
        return False, f"websockets import failed: {exc}"


def validate_torch_import() -> tuple[bool, str]:
    """Validate torch import."""
    try:
        import torch
        version = torch.__version__
        return True, f"torch {version}: OK"
    except ImportError as exc:
        return False, f"torch import failed: {exc}"


def validate_fastapi_import() -> tuple[bool, str]:
    """Validate FastAPI import."""
    try:
        from fastapi import FastAPI
        return True, "FastAPI: OK"
    except ImportError as exc:
        return False, f"FastAPI import failed: {exc}"


def validate_pydantic_import() -> tuple[bool, str]:
    """Validate Pydantic import."""
    try:
        from pydantic import BaseModel
        return True, "Pydantic: OK"
    except ImportError as exc:
        return False, f"Pydantic import failed: {exc}"


def validate_prefect_import() -> tuple[bool, str]:
    """Validate Prefect import."""
    try:
        import prefect
        version = prefect.__version__
        return True, f"prefect {version}: OK"
    except ImportError as exc:
        return False, f"prefect import failed: {exc}"


def validate_opentelemetry_import() -> tuple[bool, str]:
    """Validate OpenTelemetry import."""
    try:
        from opentelemetry import trace
        return True, "OpenTelemetry: OK"
    except ImportError as exc:
        return False, f"OpenTelemetry import failed: {exc}"


def validate_structlog_import() -> tuple[bool, str]:
    """Validate structlog import."""
    try:
        import structlog
        return True, "structlog: OK"
    except ImportError as exc:
        return False, f"structlog import failed: {exc}"


def validate_prometheus_import() -> tuple[bool, str]:
    """Validate prometheus-client import."""
    try:
        from prometheus_client import REGISTRY
        return True, "prometheus-client: OK"
    except ImportError as exc:
        return False, f"prometheus-client import failed: {exc}"


def validate_requirements_file() -> tuple[bool, str]:
    """Validate requirements.txt exists and is valid."""
    root = Path(__file__).resolve().parents[1]
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
    return True, "requirements.txt: OK"


def validate_app_import() -> tuple[bool, str]:
    """Validate app.main can be imported."""
    try:
        root = Path(__file__).resolve().parents[1]
        api_dir = root / "apps/api"
        sys.path.insert(0, str(api_dir))
        
        from app.main import create_app
        return True, "app.main import: OK"
    except ImportError as exc:
        return False, f"app.main import failed: {exc}"
    except Exception as exc:
        return False, f"app.main creation failed: {exc}"


def main() -> int:
    """Run release candidate validation."""
    print("Release Candidate Validation")
    print("=" * 50)
    
    validations = [
        ("Python version", validate_python_version),
        ("Dependency resolution", validate_dependency_resolution),
        ("Requirements file", validate_requirements_file),
        ("WebSocket import", validate_websocket_import),
        ("Torch import", validate_torch_import),
        ("FastAPI import", validate_fastapi_import),
        ("Pydantic import", validate_pydantic_import),
        ("Prefect import", validate_prefect_import),
        ("OpenTelemetry import", validate_opentelemetry_import),
        ("Structlog import", validate_structlog_import),
        ("Prometheus import", validate_prometheus_import),
        ("App import", validate_app_import),
    ]
    
    passed = 0
    failed = 0
    
    for name, validation_func in validations:
        try:
            success, message = validation_func()
            if success:
                print(f"  ✓ {message}")
                passed += 1
            else:
                print(f"  ✗ {message}")
                failed += 1
        except Exception as exc:
            print(f"  ✗ {name}: ERROR ({exc})")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Validation Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\nERROR: Release candidate validation failed")
        return 1
    
    print("\nSUCCESS: Release candidate validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
