"""test_control_plane_api.py — v0.8.8 /control-plane endpoint tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# ── Response shape ────────────────────────────────────────────────────────────

def test_control_plane_returns_200(client):
    response = client.get("/control-plane")
    assert response.status_code == 200


def test_control_plane_content_type_json(client):
    response = client.get("/control-plane")
    assert "application/json" in response.headers["content-type"]


def test_control_plane_has_required_fields(client):
    data = client.get("/control-plane").json()
    required = [
        "open_positions", "closed_positions",
        "session_realized_pnl", "session_unrealized_pnl", "session_total_pnl",
        "total_balance", "available_balance", "current_balance", "session_start_balance",
        "claim_status", "claim_available", "claimed_amount",
        "release_ready", "live_applied_testing_ready",
        "live_mode_ui_blocked", "blocked_reason_messages",
    ]
    for field in required:
        assert field in data, f"Missing field: {field}"


# ── Positions ─────────────────────────────────────────────────────────────────

def test_open_positions_is_list(client):
    data = client.get("/control-plane").json()
    assert isinstance(data["open_positions"], list)


def test_closed_positions_is_list(client):
    data = client.get("/control-plane").json()
    assert isinstance(data["closed_positions"], list)


def test_open_positions_empty_by_default(client):
    data = client.get("/control-plane").json()
    assert data["open_positions"] == []


def test_closed_positions_empty_by_default(client):
    data = client.get("/control-plane").json()
    assert data["closed_positions"] == []


# ── Session PnL ───────────────────────────────────────────────────────────────

def test_session_realized_pnl_default_zero(client):
    data = client.get("/control-plane").json()
    assert data["session_realized_pnl"] == 0.0


def test_session_unrealized_pnl_default_zero(client):
    data = client.get("/control-plane").json()
    assert data["session_unrealized_pnl"] == 0.0


def test_session_total_pnl_default_zero(client):
    data = client.get("/control-plane").json()
    assert data["session_total_pnl"] == 0.0


# ── Balance ───────────────────────────────────────────────────────────────────

def test_total_balance_default_zero(client):
    data = client.get("/control-plane").json()
    assert data["total_balance"] == 0.0


def test_available_balance_default_zero(client):
    data = client.get("/control-plane").json()
    assert data["available_balance"] == 0.0


def test_current_balance_default_zero(client):
    data = client.get("/control-plane").json()
    assert data["current_balance"] == 0.0


def test_session_start_balance_default_zero(client):
    data = client.get("/control-plane").json()
    assert data["session_start_balance"] == 0.0


# ── Claim ─────────────────────────────────────────────────────────────────────

def test_claim_status_not_claimable_by_default(client):
    data = client.get("/control-plane").json()
    assert data["claim_status"] == "not_claimable_outcome_unknown"


def test_claim_available_false_by_default(client):
    data = client.get("/control-plane").json()
    assert data["claim_available"] is False


def test_claimed_amount_zero_by_default(client):
    data = client.get("/control-plane").json()
    assert data["claimed_amount"] == 0.0


# ── Gate invariants ───────────────────────────────────────────────────────────

def test_live_applied_testing_ready_always_false(client):
    """live_applied_testing_ready must NEVER be auto-enabled."""
    data = client.get("/control-plane").json()
    assert data["live_applied_testing_ready"] is False


def test_release_ready_true(client):
    data = client.get("/control-plane").json()
    assert data["release_ready"] is True


def test_live_mode_ui_blocked_true_when_live_not_ready(client):
    data = client.get("/control-plane").json()
    assert data["live_mode_ui_blocked"] is True


def test_blocked_reason_messages_not_empty_when_blocked(client):
    data = client.get("/control-plane").json()
    assert len(data["blocked_reason_messages"]) > 0


def test_blocked_reason_includes_turkish_message(client):
    data = client.get("/control-plane").json()
    msgs = data["blocked_reason_messages"]
    assert any("yetkilendirilmedi" in m for m in msgs)


# ── No secrets ────────────────────────────────────────────────────────────────

def test_no_secret_fields_in_response(client):
    data = client.get("/control-plane").json()
    forbidden = {"api_key", "secret", "password", "token", "credential"}
    for key in data:
        assert key.lower() not in forbidden, f"Secret-like field: {key}"
