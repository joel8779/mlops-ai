"""Container health diagnostic utility.

Validates that container runtime is healthy.
This is a minimal-risk diagnostic tool.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def check_docker_available() -> tuple[bool, str]:
    """Check if Docker is available."""
    try:
        import subprocess
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"Docker is available: {result.stdout.strip()}"
        return False, "Docker command failed"
    except FileNotFoundError:
        return False, "Docker is not installed or not in PATH"
    except Exception as exc:
        return False, f"Docker check failed: {exc}"


def check_docker_compose_available() -> tuple[bool, str]:
    """Check if Docker Compose is available."""
    try:
        import subprocess
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"Docker Compose is available: {result.stdout.strip()}"
        return False, "Docker Compose command failed"
    except FileNotFoundError:
        return False, "Docker Compose is not installed or not in PATH"
    except Exception as exc:
        return False, f"Docker Compose check failed: {exc}"


def check_dockerfile_exists() -> tuple[bool, str]:
    """Check if Dockerfile exists."""
    root = Path(__file__).resolve().parents[2]
    dockerfile = root / "apps/api/Dockerfile"
    
    if dockerfile.exists():
        return True, f"Dockerfile exists at {dockerfile}"
    return False, f"Dockerfile not found at {dockerfile}"


def check_docker_compose_files() -> tuple[bool, str]:
    """Check if Docker Compose files exist."""
    root = Path(__file__).resolve().parents[2]
    
    compose_files = [
        root / "docker-compose.yml",
        root / "docker-compose.dev.yml",
        root / "docker-compose.prod.yml",
    ]
    
    missing = []
    for compose_file in compose_files:
        if not compose_file.exists():
            missing.append(compose_file.name)
    
    if missing:
        return False, f"Missing Docker Compose files: {', '.join(missing)}"
    return True, "All Docker Compose files exist"


def main() -> int:
    """Run container health diagnostics."""
    print("Running container health diagnostics...")
    
    checks = [
        check_docker_available(),
        check_docker_compose_available(),
        check_dockerfile_exists(),
        check_docker_compose_files(),
    ]
    
    errors = []
    for passed, message in checks:
        if passed:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")
            errors.append(message)
    
    if errors:
        print(f"\nERROR: {len(errors)} container health issues found")
        print("\nRemediation suggestions:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\nContainer health diagnostics: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
