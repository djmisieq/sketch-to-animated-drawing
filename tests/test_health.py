"""Test health check endpoint."""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app


def test_health_sync():
    """Test health check endpoint with synchronous client."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_async():
    """Test health check endpoint with asynchronous client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
