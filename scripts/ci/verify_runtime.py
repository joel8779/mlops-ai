from __future__ import annotations

import importlib

from app.main import create_app


REQUIRED_IMPORTS = [
    "app.api.v1.router",
    "app.core.config",
    "app.db.session",
    "app.observability.tracing",
    "app.observability.metrics",
    "app.resilience",
    "app.services.llm.providers.gemini_provider",
    "app.services.retrieval.hybrid_retriever",
    "app.services.recommendation_service",
]


def main() -> int:
    for module_name in REQUIRED_IMPORTS:
        importlib.import_module(module_name)

    app = create_app()
    route_count = len(app.routes)
    if route_count < 10:
        print(f"Unexpectedly low FastAPI route count: {route_count}")
        return 1
    print(f"Runtime import/startup verification: OK ({route_count} app routes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
