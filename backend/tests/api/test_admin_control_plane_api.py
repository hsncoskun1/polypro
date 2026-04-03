"""Tests for GET /admin/control-plane — v0.8.9"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ENDPOINT = "/admin/control-plane"


@pytest.fixture
def response():
    return client.get(ENDPOINT)


@pytest.fixture
def data(response):
    return response.json()


# --- Response shape ---

def test_returns_200(response):
    assert response.status_code == 200


def test_content_type_json(response):
    assert "application/json" in response.headers["content-type"]


def test_has_required_fields(data):
    required = [
        "safe_stop_active", "safe_stop_reason", "scheduler_enabled",
        "global_disable_active", "config_reload_available", "config_reset_available",
        "total_balance", "available_balance", "current_balance", "session_start_balance",
        "realized_pnl", "unrealized_pnl", "session_total_pnl", "claim_adjusted_balance_effect",
        "blocked_trades", "blocked_rules", "blocked_risk_events",
        "execution_fill_events", "claim_events", "operational_alerts",
        "release_ready", "live_applied_testing_ready",
    ]
    for field in required:
        assert field in data, f"Missing field: {field}"


# --- Operational control defaults ---

def test_safe_stop_active_false(data):
    assert data["safe_stop_active"] is False


def test_safe_stop_reason_empty(data):
    assert data["safe_stop_reason"] == ""


def test_scheduler_enabled_true(data):
    assert data["scheduler_enabled"] is True


def test_global_disable_active_false(data):
    assert data["global_disable_active"] is False


def test_config_reload_available_true(data):
    assert data["config_reload_available"] is True


def test_config_reset_available_true(data):
    assert data["config_reset_available"] is True


# --- Financial defaults ---

def test_total_balance_zero(data):
    assert data["total_balance"] == 0.0


def test_available_balance_zero(data):
    assert data["available_balance"] == 0.0


def test_current_balance_zero(data):
    assert data["current_balance"] == 0.0


def test_session_start_balance_zero(data):
    assert data["session_start_balance"] == 0.0


def test_realized_pnl_zero(data):
    assert data["realized_pnl"] == 0.0


def test_unrealized_pnl_zero(data):
    assert data["unrealized_pnl"] == 0.0


def test_session_total_pnl_zero(data):
    assert data["session_total_pnl"] == 0.0


def test_claim_adjusted_balance_effect_zero(data):
    assert data["claim_adjusted_balance_effect"] == 0.0


# --- Event list defaults ---

def test_blocked_trades_empty(data):
    assert data["blocked_trades"] == []


def test_blocked_rules_empty(data):
    assert data["blocked_rules"] == []


def test_blocked_risk_events_empty(data):
    assert data["blocked_risk_events"] == []


def test_execution_fill_events_empty(data):
    assert data["execution_fill_events"] == []


def test_claim_events_empty(data):
    assert data["claim_events"] == []


def test_operational_alerts_empty(data):
    assert data["operational_alerts"] == []


# --- Release gate invariants ---

def test_release_ready_true(data):
    assert data["release_ready"] is True


def test_live_applied_testing_ready_always_false(data):
    assert data["live_applied_testing_ready"] is False


# --- Security ---

def test_no_secret_fields(data):
    secret_patterns = ["secret", "key", "token", "password", "credential", "api_key"]
    for field in data:
        for pattern in secret_patterns:
            assert pattern not in field.lower(), f"Potential secret field: {field}"
