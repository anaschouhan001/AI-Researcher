"""API integration tests over the FastAPI app (SQLite, no network)."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.database.session import init_db
from app.main import app


@pytest.fixture
async def client():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_register_login_flow(client):
    creds = {"email": "tester@example.com", "password": "supersecret1"}
    register = await client.post("/api/v1/auth/register", json=creds)
    assert register.status_code in (201, 409)  # 409 when re-run against same db

    login = await client.post("/api/v1/auth/login", json=creds)
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token

    bad_login = await client.post(
        "/api/v1/auth/login", json={**creds, "password": "wrongpassword"}
    )
    assert bad_login.status_code == 401


async def test_research_validation(client):
    response = await client.post("/api/v1/research", json={"topic": "ab"})
    assert response.status_code == 422  # topic too short

    response = await client.post(
        "/api/v1/research", json={"topic": "Valid topic", "depth": "nonsense"}
    )
    assert response.status_code == 422


async def test_get_unknown_job_404(client):
    response = await client.get("/api/v1/research/does-not-exist")
    assert response.status_code == 404
