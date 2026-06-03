import json

from app.core.paths import get_repo_root_cached
from prometheus_client import REGISTRY



def test_required_aiops_metrics_are_registered():
    names = set()
    for metric in REGISTRY.collect():
        names.add(metric.name)
        for sample in metric.samples:
            names.add(sample.name)

    assert any(name.startswith("llm_request_latency_ms") for name in names)
    assert any(name.startswith("retrieval_topk_latency_ms") for name in names)
    assert any(name.startswith("agent_execution_failures") for name in names)
    assert any(name.startswith("websocket_active_connections") for name in names)


def test_grafana_dashboards_are_valid_json():
    root = get_repo_root_cached() / "infra" / "grafana" / "dashboards"
    dashboards = list(root.glob("*.json"))

    assert dashboards
    for dashboard in dashboards:
        payload = json.loads(dashboard.read_text(encoding="utf-8"))
        assert payload["title"]
        assert payload["panels"]
