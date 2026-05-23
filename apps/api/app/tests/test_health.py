import pytest


@pytest.mark.asyncio
async def test_ready(async_client):
    response = await async_client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
