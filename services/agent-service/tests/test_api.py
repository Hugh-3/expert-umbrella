import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.storage.database import db, Database
import tempfile
from pathlib import Path

@pytest_asyncio.fixture
async def client():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    test_db = Database(db_path)
    await test_db.initialize()
    
    original_db = db
    from app import storage
    storage.database.db = test_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    db_path.unlink(missing_ok=True)
    storage.database.db = original_db

@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["version"] == "0.1.0"

@pytest.mark.asyncio
async def test_list_evaluations_empty(client):
    response = await client.get("/evaluations")
    assert response.status_code == 200
    assert "evaluations" in response.json()

@pytest.mark.asyncio
async def test_get_latest_evaluation_empty(client):
    response = await client.get("/evaluations/latest")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_trend_data(client):
    response = await client.get("/reports/trends?metric=overall&days=7")
    assert response.status_code == 200
    data = response.json()
    assert "metric" in data
    assert data["metric"] == "overall"
    assert "data" in data

@pytest.mark.asyncio
async def test_report_summary_empty(client):
    response = await client.get("/reports/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_evaluations"] == 0

@pytest.mark.asyncio
async def test_export_report_empty(client):
    response = await client.get("/reports/export")
    assert response.status_code == 200
    assert "text/markdown" in response.headers["content-type"]
