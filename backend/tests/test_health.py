from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_version():
    response = client.get("/health")
    assert response.json()["version"] == "0.1.1"


def test_health_returns_status():
    response = client.get("/health")
    assert response.json()["status"] == "ok"
