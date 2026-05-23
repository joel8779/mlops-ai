"""Test metrics export validation.

Validates that metrics are correctly exported and registered.
This is a minimal-risk validation that checks metrics health.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add apps/api to Python path
root = Path(__file__).resolve().parents[2]
api_dir = root / "apps/api"
sys.path.insert(0, str(api_dir))


def test_prometheus_registry_exists() -> bool:
    """Test that Prometheus REGISTRY can be imported."""
    try:
        from prometheus_client import REGISTRY
        return True
    except ImportError:
        return False


def test_metrics_registration() -> bool:
    """Test that metrics can be registered."""
    try:
        from prometheus_client import Counter, Histogram, Gauge
        from prometheus_client import REGISTRY
        
        # Test creating a counter
        test_counter = Counter("test_counter", "A test counter")
        test_counter.inc()
        
        # Test creating a histogram
        test_histogram = Histogram("test_histogram", "A test histogram")
        test_histogram.observe(1.0)
        
        # Test creating a gauge
        test_gauge = Gauge("test_gauge", "A test gauge")
        test_gauge.set(1.0)
        
        # Verify metrics are in registry
        metric_names = {sample.name for metric in REGISTRY.collect() for sample in metric.samples}
        return "test_counter" in metric_names and "test_histogram" in metric_names and "test_gauge" in metric_names
    except Exception:
        return False


def test_no_duplicate_registration() -> bool:
    """Test that duplicate metric registration is handled."""
    try:
        from prometheus_client import Counter, REGISTRY
        from prometheus_client.registry import CollectorRegistry
        
        # Create a custom registry to avoid conflicts
        custom_registry = CollectorRegistry()
        
        # Register a metric twice should raise an error
        counter1 = Counter("duplicate_test", "Test", registry=custom_registry)
        try:
            counter2 = Counter("duplicate_test", "Test", registry=custom_registry)
            return False  # Should have raised an error
        except ValueError:
            return True  # Expected behavior
    except Exception:
        return False


def main() -> int:
    """Run metrics export validation."""
    print("Testing metrics export...")
    
    tests = [
        ("Prometheus REGISTRY exists", test_prometheus_registry_exists),
        ("Metrics registration", test_metrics_registration),
        ("No duplicate registration", test_no_duplicate_registration),
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
    
    print(f"\nMetrics export validation: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
