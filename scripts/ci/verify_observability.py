from __future__ import annotations

import json
from pathlib import Path

from prometheus_client import REGISTRY

from app.main import create_app


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
    return {sample.name for metric in REGISTRY.collect() for sample in metric.samples}


def validate_dashboards() -> list[str]:
    root = Path("infra/grafana/dashboards")
    errors: list[str] = []
    if not root.exists():
        return ["infra/grafana/dashboards does not exist"]
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
    app = create_app()
    paths = {route.path for route in app.routes}
    if "/metrics" not in paths:
        print("Prometheus endpoint /metrics is not registered")
        return 1

    names = metric_names()
    missing = sorted(metric for metric in REQUIRED_METRICS if not any(name.startswith(metric) for name in names))
    dashboard_errors = validate_dashboards()
    if missing or dashboard_errors:
        if missing:
            print("Missing required metrics:")
            for metric in missing:
                print(f"  - {metric}")
        for error in dashboard_errors:
            print(error)
        return 1

    print("Observability registration: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
