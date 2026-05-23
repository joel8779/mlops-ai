from __future__ import annotations

import importlib
import sys

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
    failed_imports = []
    for module_name in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module_name)
        except ImportError as exc:
            failed_imports.append((module_name, str(exc)))
            print(f"WARNING: Failed to import {module_name}: {exc}")
        except Exception as exc:
            failed_imports.append((module_name, str(exc)))
            print(f"WARNING: Error importing {module_name}: {exc}")

    if failed_imports:
        print(f"ERROR: {len(failed_imports)} required imports failed")
        for module_name, error in failed_imports:
            print(f"  - {module_name}: {error}")
        return 1

    try:
        app = create_app()
        route_count = len(app.routes)
        if route_count < 10:
            print(f"ERROR: Unexpectedly low FastAPI route count: {route_count}")
            return 1
        print(f"Runtime import/startup verification: OK ({route_count} app routes)")
        return 0
    except Exception as exc:
        print(f"ERROR: Failed to create app: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
