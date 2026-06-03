from __future__ import annotations

import json
import sys
from pathlib import Path

# Optional imports with graceful degradation
try:
    from prometheus_client import REGISTRY
except ImportError as exc:
    print(f"ERROR: Failed to import prometheus_client: {exc}")
    print("Remediation: Ensure prometheus-client is installed via requirements-dev.txt")
    sys.exit(1)

try:
    from app.main import create_app
except ImportError as exc:
    print(f"ERROR: Failed to import app.main: {exc}")
    print("This usually indicates missing dependencies or import errors.")
    sys.exit(1)


REQUIRED_METRICS = {
    "llm_request_latency_ms",
    "llm_tokens_input",
    "llm_tokens_output",
    "llm_failures",
    "llm_estimated_cost_usd",
    "recommendation_generation_time_ms",
    "retrieval_topk_latency_ms",
    "websocket_active_connections",
    "redis_stream_consumer_lag",
    "agent_execution_failures",
    "embedding_generation_duration_ms",
}


def metric_names() -> set[str]:
    names = set()
    for metric in REGISTRY.collect():
        names.add(metric.name)
        for sample in metric.samples:
            names.add(sample.name)
    return names


def validate_dashboards() -> list[str]:
    root = Path("infra/grafana/dashboards")
    errors: list[str] = []
    if not root.exists():
        # Dashboard directory is optional for CI
        return []
    for dashboard in root.glob("*.json"):
        try:
            data = json.loads(dashboard.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{dashboard}: invalid JSON: {exc}")
            continue
        if not data.get("title"):
            errors.append(f"{dashboard}: missing title")
        if not data.get("panels"):
            errors.append(f"{dashboard}: missing panels")
    return errors


def main() -> int:
    try:
        app = create_app()
    except Exception as exc:
        print(f"ERROR: Failed to create app: {exc}")
        import traceback
        traceback.print_exc()
        return 1

    paths = {route.path for route in app.routes}
    if "/metrics" not in paths:
        print("ERROR: Prometheus endpoint /metrics is not registered")
        return 1

    names = metric_names()
    missing = sorted(metric for metric in REQUIRED_METRICS if not any(name.startswith(metric) for name in names))
    dashboard_errors = validate_dashboards()
    
    if missing:
        print("ERROR: Missing required metrics:")
        for metric in missing:
            print(f"  - {metric}")
        return 1
    
    if dashboard_errors:
        print("WARNING: Dashboard validation errors (non-blocking):")
        for error in dashboard_errors:
            print(f"  - {error}")

    print("Observability registration: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
