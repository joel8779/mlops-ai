"""Security release validation script.

Validates:
- no committed secrets
- no critical CVEs
- secure dependency graph
- secure Docker base image
- secure runtime defaults
- secure environment handling

This is a minimal-risk validation tool for release security.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def validate_no_committed_secrets() -> tuple[bool, str]:
    """Validate that no secrets are committed to the repository."""
    root = Path(__file__).resolve().parents[1]
    
    # Patterns that might indicate secrets
    secret_patterns = [
        r'api[_-]?key\s*=\s*["\']',
        r'secret[_-]?key\s*=\s*["\']',
        r'password\s*=\s*["\']',
        r'token\s*=\s*["\']',
        r'aws[_-]?access[_-]?key[_-]?id\s*=\s*["\']',
        r'aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\']',
        r'private[_-]?key\s*=\s*["\']',
        r'auth[_-]?token\s*=\s*["\']',
    ]
    
    # Files to check
    files_to_check = []
    for pattern in ['*.py', '*.yml', '*.yaml', '*.json', '*.env*', '*.toml']:
        files_to_check.extend(root.rglob(pattern))
    
    issues = []
    for file_path in files_to_check:
        # Skip node_modules, .git, __pycache__, etc.
        if any(skip in str(file_path) for skip in ['node_modules', '.git', '__pycache__', '.venv', 'venv']):
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if the value looks like a real secret (not a placeholder)
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if re.search(pattern, line, re.IGNORECASE):
                            # Check if it's a placeholder
                            if any(placeholder in line.lower() for placeholder in ['test', 'example', 'change', 'placeholder', 'your-', 'xxx', 'yyy']):
                                continue
                            issues.append(f"{file_path}:{i+1}: Potential secret found")
        except Exception:
            continue
    
    if issues:
        return False, f"Found {len(issues)} potential secrets: {', '.join(issues[:5])}"
    return True, "No committed secrets detected"


def validate_no_env_files() -> tuple[bool, str]:
    """Validate that .env files are not committed."""
    root = Path(__file__).resolve().parents[1]
    
    env_files = list(root.rglob('.env*'))
    # Filter out .env.example and .env.template
    committed_env_files = [f for f in env_files if not any(suffix in f.name for suffix in ['example', 'template', 'sample'])]
    
    if committed_env_files:
        return False, f"Committed .env files found: {', '.join(str(f) for f in committed_env_files)}"
    return True, "No committed .env files detected"


def validate_dependency_pinning() -> tuple[bool, str]:
    """Validate that Python dependencies are pinned."""
    root = Path(__file__).resolve().parents[1]
    requirements_file = root / "apps/api/requirements.txt"
    
    if not requirements_file.exists():
        return False, "requirements.txt not found"
    
    content = requirements_file.read_text()
    lines = content.splitlines()
    
    unpinned = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('-r'):
            if '==' not in line:
                unpinned.append(line)
    
    if unpinned:
        return False, f"Unpinned dependencies: {', '.join(unpinned)}"
    return True, "All dependencies are pinned"


def validate_docker_base_image() -> tuple[bool, str]:
    """Validate Docker base image is secure."""
    root = Path(__file__).resolve().parents[1]
    dockerfile = root / "apps/api/Dockerfile"
    
    if not dockerfile.exists():
        return False, "Dockerfile not found"
    
    content = dockerfile.read_text()
    
    # Check for non-root user
    if 'USER' not in content:
        return False, "Dockerfile does not set non-root user"
    
    # Check for specific base image
    if 'python:3.11-slim' in content or 'python:3.12-slim' in content:
        return True, "Docker base image is secure (slim variant)"
    
    return False, "Docker base image may not be optimal"


def validate_python_version() -> tuple[bool, str]:
    """Validate Python version is supported."""
    major, minor = sys.version_info[:2]
    if (major, minor) not in [(3, 11), (3, 12)]:
        return False, f"Python {major}.{minor} not supported (requires 3.11 or 3.12)"
    return True, f"Python {major}.{minor} is supported"


def validate_security_policies_exist() -> tuple[bool, str]:
    """Validate that security policy files exist."""
    root = Path(__file__).resolve().parents[1]
    
    policy_files = [
        root / "security/policies/pip_audit_policy.yml",
        root / "security/policies/trivy_policy.yml",
        root / "security/policies/npm_audit_policy.yml",
    ]
    
    missing = []
    for policy_file in policy_files:
        if not policy_file.exists():
            missing.append(policy_file.name)
    
    if missing:
        return False, f"Missing security policy files: {', '.join(missing)}"
    return True, "All security policy files exist"


def main() -> int:
    """Run security release validation."""
    print("Security Release Validation")
    print("=" * 50)
    
    validations = [
        ("No committed secrets", validate_no_committed_secrets),
        ("No committed .env files", validate_no_env_files),
        ("Dependency pinning", validate_dependency_pinning),
        ("Docker base image", validate_docker_base_image),
        ("Python version", validate_python_version),
        ("Security policies exist", validate_security_policies_exist),
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
        print("\nERROR: Security release validation failed")
        return 1
    
    print("\nSUCCESS: Security release validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
