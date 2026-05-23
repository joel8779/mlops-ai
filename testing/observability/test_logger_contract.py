"""Test logger contract validation.

Validates that structured logging works correctly.
This is a minimal-risk validation that checks logging health.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add apps/api to Python path
root = Path(__file__).resolve().parents[2]
api_dir = root / "apps/api"
sys.path.insert(0, str(api_dir))


def test_structlog_import() -> bool:
    """Test that structlog can be imported."""
    try:
        import structlog
        return True
    except ImportError:
        return False


def test_logger_creation() -> bool:
    """Test that a logger can be created."""
    try:
        import structlog
        
        logger = structlog.get_logger(__name__)
        return logger is not None
    except Exception:
        return False


def test_logger_binding() -> bool:
    """Test that context can be bound to logger."""
    try:
        import structlog
        
        logger = structlog.get_logger(__name__)
        bound_logger = logger.bind(key="value")
        return bound_logger is not None
    except Exception:
        return False


def test_json_renderer() -> bool:
    """Test that JSON renderer works."""
    try:
        import structlog
        import structlog.processors
        
        renderer = structlog.processors.JSONRenderer()
        return renderer is not None
    except Exception:
        return False


def test_console_renderer() -> bool:
    """Test that console renderer works."""
    try:
        import structlog
        import structlog.dev
        
        renderer = structlog.dev.ConsoleRenderer()
        return renderer is not None
    except Exception:
        return False


def main() -> int:
    """Run logger contract validation."""
    print("Testing logger contract...")
    
    tests = [
        ("Structlog import", test_structlog_import),
        ("Logger creation", test_logger_creation),
        ("Logger binding", test_logger_binding),
        ("JSON renderer", test_json_renderer),
        ("Console renderer", test_console_renderer),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        if test_func():
            print(f"  ✓ {test_name}")
            passed += 1
        else:
            print(f"  ✗ {test_name}")
            failed += 1
    
    print(f"\nLogger contract validation: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
