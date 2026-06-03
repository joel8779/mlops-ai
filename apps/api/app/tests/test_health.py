import pytest


@pytest.mark.asyncio
async def test_ready(test_client, monkeypatch):
    async def mock_readiness_payload():
        return {
            "status": "ready",
            "service": "test-service",
            "version": "0.1.0",
            "dependencies": {}
        }
    monkeypatch.setattr("app.main._readiness_payload", mock_readiness_payload)
    response = await test_client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

