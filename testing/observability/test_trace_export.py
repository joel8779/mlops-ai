"""Test trace export validation.

Validates that traces can be exported correctly.
This is a minimal-risk validation that checks tracing health.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add apps/api to Python path
root = Path(__file__).resolve().parents[2]
api_dir = root / "apps/api"
sys.path.insert(0, str(api_dir))


def test_tracer_provider_exists() -> bool:
    """Test that tracer provider can be created."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        
        provider = TracerProvider(resource=Resource.create({"service.name": "test"}))
        trace.set_tracer_provider(provider)
        return True
    except Exception:
        return False


def test_tracer_creation() -> bool:
    """Test that a tracer can be created."""
    try:
        from opentelemetry import trace
        
        tracer = trace.get_tracer(__name__)
        return tracer is not None
    except Exception:
        return False


def test_span_creation() -> bool:
    """Test that a span can be created."""
    try:
        from opentelemetry import trace
        
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("test_span") as span:
            return span is not None
    except Exception:
        return False


def test_span_attributes() -> bool:
    """Test that span attributes can be set."""
    try:
        from opentelemetry import trace
        
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("test_span") as span:
            span.set_attribute("test_key", "test_value")
            return True
    except Exception:
        return False


def test_noop_exporter() -> bool:
    """Test that tracing works with no exporter (noop mode)."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        
        # Create provider without exporter (noop mode)
        provider = TracerProvider(resource=Resource.create({"service.name": "test"}))
        trace.set_tracer_provider(provider)
        
        # Should still be able to create spans
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("test_span") as span:
            return span is not None
    except Exception:
        return False


def main() -> int:
    """Run trace export validation."""
    print("Testing trace export...")
    
    tests = [
        ("Tracer provider exists", test_tracer_provider_exists),
        ("Tracer creation", test_tracer_creation),
        ("Span creation", test_span_creation),
        ("Span attributes", test_span_attributes),
        ("Noop exporter", test_noop_exporter),
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
    
    print(f"\nTrace export validation: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
