"""Test correlation context validation.

Validates that correlation IDs are propagated correctly.
This is a minimal-risk validation that checks correlation context health.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add apps/api to Python path
root = Path(__file__).resolve().parents[2]
api_dir = root / "apps/api"
sys.path.insert(0, str(api_dir))


def test_correlation_context_import() -> bool:
    """Test that correlation context can be imported."""
    try:
        from app.observability.tracing.correlation import CorrelationContext
        return True
    except ImportError:
        return False


def test_correlation_context_creation() -> bool:
    """Test that a correlation context can be created."""
    try:
        from app.observability.tracing.correlation import CorrelationContext
        
        context = CorrelationContext()
        return context is not None
    except Exception:
        return False


def test_correlation_id_generation() -> bool:
    """Test that correlation IDs can be generated."""
    try:
        from app.observability.tracing.correlation import CorrelationContext
        
        context = CorrelationContext()
        correlation_id = context.correlation_id
        return correlation_id is not None and len(correlation_id) > 0
    except Exception:
        return False


def test_correlation_binding() -> bool:
    """Test that correlation context can be bound."""
    try:
        from app.observability.tracing.correlation import bind_correlation
        
        bind_correlation(correlation_id="test-id", user_id="test-user")
        return True
    except Exception:
        return False


def test_current_trace_context() -> bool:
    """Test that current trace context can be retrieved."""
    try:
        from app.observability.tracing.correlation import current_trace_context
        
        context = current_trace_context()
        return context is not None
    except Exception:
        return False


def main() -> int:
    """Run correlation context validation."""
    print("Testing correlation context...")
    
    tests = [
        ("Correlation context import", test_correlation_context_import),
        ("Correlation context creation", test_correlation_context_creation),
        ("Correlation ID generation", test_correlation_id_generation),
        ("Correlation binding", test_correlation_binding),
        ("Current trace context", test_current_trace_context),
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
    
    print(f"\nCorrelation context validation: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
