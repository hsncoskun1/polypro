import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

MARKET_PAYLOAD = {"market_id": "mkt-001", "title": "Test Market", "timeframe": "1W"}


@pytest.fixture()
def client(tmp_path):
    os.environ["MARKET_STORE_PATH"] = str(tmp_path / "test_markets.json")
    with TestClient(app) as c:
        yield c
    os.environ.pop("MARKET_STORE_PATH", None)


# ── POST /api/v1/markets ──────────────────────────────────────────────────────

def test_create_market_returns_201(client):
    response = client.post("/api/v1/markets", json=MARKET_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["market_id"] == "mkt-001"
    assert data["title"] == "Test Market"
    assert data["timeframe"] == "1W"
    assert data["status"] == "active"


def test_create_market_duplicate_returns_409(client):
    client.post("/api/v1/markets", json=MARKET_PAYLOAD)
    response = client.post("/api/v1/markets", json=MARKET_PAYLOAD)
    assert response.status_code == 409
    assert "mkt-001" in response.json()["detail"]


def test_create_market_invalid_timeframe_returns_422(client):
    payload = {**MARKET_PAYLOAD, "market_id": "mkt-bad", "timeframe": "INVALID"}
    response = client.post("/api/v1/markets", json=payload)
    assert response.status_code == 422
    assert "INVALID" in response.json()["detail"]


# ── GET /api/v1/markets ───────────────────────────────────────────────────────

def test_list_markets_returns_added_market(client):
    client.post("/api/v1/markets", json=MARKET_PAYLOAD)
    response = client.get("/api/v1/markets")
    assert response.status_code == 200
    assert any(m["market_id"] == "mkt-001" for m in response.json())


def test_list_markets_empty(client):
    response = client.get("/api/v1/markets")
    assert response.status_code == 200
    assert response.json() == []


# ── GET /api/v1/markets/active ────────────────────────────────────────────────

def test_list_active_markets_filters_inactive(client):
    client.post("/api/v1/markets", json=MARKET_PAYLOAD)
    client.post("/api/v1/markets", json={**MARKET_PAYLOAD, "market_id": "mkt-002"})
    client.patch("/api/v1/markets/mkt-002/status", json={"status": "inactive"})
    response = client.get("/api/v1/markets/active")
    assert response.status_code == 200
    ids = [m["market_id"] for m in response.json()]
    assert "mkt-001" in ids
    assert "mkt-002" not in ids


# ── GET /api/v1/markets/{market_id} ──────────────────────────────────────────

def test_get_market_returns_200(client):
    client.post("/api/v1/markets", json=MARKET_PAYLOAD)
    response = client.get("/api/v1/markets/mkt-001")
    assert response.status_code == 200
    assert response.json()["market_id"] == "mkt-001"


def test_get_market_not_found_returns_404(client):
    response = client.get("/api/v1/markets/nonexistent")
    assert response.status_code == 404
    assert "nonexistent" in response.json()["detail"]


# ── PATCH /api/v1/markets/{market_id}/status ─────────────────────────────────

def test_update_status_returns_updated_market(client):
    client.post("/api/v1/markets", json=MARKET_PAYLOAD)
    response = client.patch("/api/v1/markets/mkt-001/status", json={"status": "inactive"})
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"


def test_update_status_not_found_returns_404(client):
    response = client.patch("/api/v1/markets/nonexistent/status", json={"status": "inactive"})
    assert response.status_code == 404


# ── contract hardening ────────────────────────────────────────────────────────

def test_list_markets_order_is_deterministic(client):
    client.post("/api/v1/markets", json={**MARKET_PAYLOAD, "market_id": "mkt-003"})
    client.post("/api/v1/markets", json={**MARKET_PAYLOAD, "market_id": "mkt-001"})
    client.post("/api/v1/markets", json={**MARKET_PAYLOAD, "market_id": "mkt-002"})
    response = client.get("/api/v1/markets")
    assert response.status_code == 200
    ids = [m["market_id"] for m in response.json()]
    assert ids == ["mkt-001", "mkt-002", "mkt-003"]


def test_list_active_order_is_deterministic(client):
    client.post("/api/v1/markets", json={**MARKET_PAYLOAD, "market_id": "mkt-003"})
    client.post("/api/v1/markets", json={**MARKET_PAYLOAD, "market_id": "mkt-001"})
    client.post("/api/v1/markets", json={**MARKET_PAYLOAD, "market_id": "mkt-002"})
    client.patch("/api/v1/markets/mkt-002/status", json={"status": "inactive"})
    response = client.get("/api/v1/markets/active")
    assert response.status_code == 200
    ids = [m["market_id"] for m in response.json()]
    assert ids == ["mkt-001", "mkt-003"]


def test_update_status_invalid_value_returns_422(client):
    client.post("/api/v1/markets", json=MARKET_PAYLOAD)
    response = client.patch("/api/v1/markets/mkt-001/status", json={"status": "INVALID"})
    assert response.status_code == 422


def test_create_market_missing_required_field_returns_422(client):
    response = client.post("/api/v1/markets", json={"title": "No ID", "timeframe": "1W"})
    assert response.status_code == 422


def test_create_market_empty_body_returns_422(client):
    response = client.post("/api/v1/markets", json={})
    assert response.status_code == 422


# ── persistence integration ───────────────────────────────────────────────────

def test_market_persists_across_restart(tmp_path):
    store_path = str(tmp_path / "markets.json")
    os.environ["MARKET_STORE_PATH"] = store_path
    try:
        with TestClient(app) as c:
            c.post("/api/v1/markets", json=MARKET_PAYLOAD)
        with TestClient(app) as c:
            response = c.get("/api/v1/markets/mkt-001")
            assert response.status_code == 200
            assert response.json()["market_id"] == "mkt-001"
    finally:
        os.environ.pop("MARKET_STORE_PATH", None)
