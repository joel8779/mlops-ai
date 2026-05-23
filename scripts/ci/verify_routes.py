from __future__ import annotations

from app.api.v1.router import api_router


REQUIRED_ROUTES = {
    "/ai/copilot",
    "/ai/copilot-2",
    "/recommendations/candidates",
    "/billing/plans",
    "/search/candidates",
    "/ws/{organization_id}",
}


def main() -> int:
    paths = {route.path for route in api_router.routes}
    missing = sorted(REQUIRED_ROUTES - paths)
    if missing:
        print("Missing required routes:")
        for route in missing:
            print(f"  - {route}")
        return 1
    print(f"Route registration: OK ({len(paths)} routes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
