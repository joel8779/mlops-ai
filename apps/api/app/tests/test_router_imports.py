import pytest


@pytest.mark.smoke
def test_api_router_imports_with_phase_five_routes():
    from app.api.v1.router import api_router

    paths = {route.path for route in api_router.routes}

    assert "/ai/copilot-2" in paths
    assert "/recommendations/candidates" in paths
    assert "/billing/plans" in paths
