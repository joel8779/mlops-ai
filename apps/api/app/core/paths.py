"""
Centralized path utilities for runtime-safe path resolution.

This module provides platform-independent path resolution that works across:
- Windows local development
- Docker Linux containers
- CI runners
- Production deployment

The key insight is that hardcoded parent traversal (e.g., .parents[4]) fails
because path depth varies between environments. Instead, we use multiple
strategies to find the repo root reliably.
"""

import os
from pathlib import Path
from typing import Optional


def get_repo_root() -> Path:
    """
    Get the repository root directory using multiple fallback strategies.

    Strategies (in order of preference):
    1. Environment variable REPO_ROOT (explicit override)
    2. Git root detection (if in a git repository)
    3. Marker file detection (looking for pyproject.toml, .git, etc.)
    4. Fallback to current working directory

    Returns:
        Path: The repository root directory

    Raises:
        RuntimeError: If repo root cannot be determined
    """
    # Strategy 1: Environment variable override
    repo_root_env = os.environ.get("REPO_ROOT")
    if repo_root_env:
        return Path(repo_root_env).resolve()

    # Strategy 2: Git root detection
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip()).resolve()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    # Strategy 3: Marker file detection
    # Start from the current file and search upwards for repo markers
    current_path = Path(__file__).resolve()
    repo_markers = [
        "pyproject.toml",
        ".git",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "docker-compose.yml",
    ]

    for _ in range(20):  # Limit search depth to prevent infinite loops
        if any((current_path / marker).exists() for marker in repo_markers):
            return current_path

        parent = current_path.parent
        if parent == current_path:  # Reached filesystem root
            break
        current_path = parent

    # Strategy 4: Fallback to current working directory
    # This is a safe fallback for Docker containers where CWD is typically /app
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").exists() or (cwd / "app").exists():
        return cwd

    # If all strategies fail, raise an error
    raise RuntimeError(
        "Could not determine repository root. "
        "Set REPO_ROOT environment variable or ensure you're in a git repository."
    )


def get_cache_dir(subpath: str = "runtime") -> Path:
    """
    Get the cache directory path.

    Args:
        subpath: Subdirectory within the cache directory

    Returns:
        Path: The cache directory path
    """
    repo_root = get_repo_root()
    cache_dir = repo_root / subpath
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_model_cache_dir() -> Path:
    """
    Get the model cache directory for HuggingFace models.

    Returns:
        Path: The model cache directory path
    """
    return get_cache_dir("runtime/model-cache/huggingface")


def get_data_dir(subpath: str = "data") -> Path:
    """
    Get the data directory path.

    Args:
        subpath: Subdirectory within the data directory

    Returns:
        Path: The data directory path
    """
    repo_root = get_repo_root()
    data_dir = repo_root / subpath
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def resolve_relative_path(relative_path: str) -> Path:
    """
    Resolve a relative path from the repository root.

    Args:
        relative_path: Relative path from repo root

    Returns:
        Path: The resolved absolute path
    """
    repo_root = get_repo_root()
    return repo_root / relative_path


# Singleton instance for performance
_repo_root_cache: Optional[Path] = None


def get_repo_root_cached() -> Path:
    """
    Get the repository root directory with caching.

    This is a performance-optimized version that caches the result
    after the first call.

    Returns:
        Path: The repository root directory
    """
    global _repo_root_cache
    if _repo_root_cache is None:
        _repo_root_cache = get_repo_root()
    return _repo_root_cache
