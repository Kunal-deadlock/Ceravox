"""Health endpoint contract tests."""

import httpx
import pytest

from app.main import app


@pytest.fixture
async def client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_live_returns_live_status(client: httpx.AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "live"}


@pytest.mark.asyncio
async def test_ready_returns_ready_when_dependencies_are_available(
    client: httpx.AsyncClient,
) -> None:
    app.state.readiness_checks = {"runtime": lambda: True}

    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "dependencies": {"runtime": "available"},
    }


@pytest.mark.asyncio
async def test_ready_returns_503_when_dependency_is_unavailable(
    client: httpx.AsyncClient,
) -> None:
    app.state.readiness_checks = {"ollama": lambda: False}

    response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "dependencies": {"ollama": "unavailable"},
    }
    app.state.readiness_checks = {}


@pytest.mark.asyncio
async def test_unknown_routes_return_json_error(client: httpx.AsyncClient) -> None:
    response = await client.get("/missing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Route not found"},
    }
