"""test_readiness_api.py — v0.8.7 /readiness endpoint tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# ── Response shape ────────────────────────────────────────────────────────────

def test_readiness_returns_200(client):
    response = client.get("/readiness")
    assert response.status_code == 200


def test_readiness_content_type_json(client):
    response = client.get("/readiness")
    assert "application/json" in response.headers["content-type"]


def test_readiness_has_required_fields(client):
    data = client.get("/readiness").json()
    required = [
        "launcher_blocked", "setup_completed", "update_required",
        "preflight_passed", "backend_ready", "final_backend_ready",
        "release_ready", "live_applied_testing_ready",
        "blocked_reason_messages", "frontend_port", "backend_port",
        "readiness_poll_interval_ms",
    ]
    for field in required:
        assert field in data, f"Missing field: {field}"


# ── Fixed invariants ─────────────────────────────────────────────────────────

def test_live_applied_testing_ready_always_false(client):
    """live_applied_testing_ready must NEVER be auto-enabled."""
    data = client.get("/readiness").json()
    assert data["live_applied_testing_ready"] is False


def test_launcher_blocked_true_when_live_not_ready(client):
    """launcher_blocked=True when live_applied_testing_ready=False."""
    data = client.get("/readiness").json()
    assert data["launcher_blocked"] is True


def test_continue_destination_none_when_blocked(client):
    """continue_destination must be None when launcher is blocked."""
    data = client.get("/readiness").json()
    assert data["continue_destination"] is None


def test_backend_ready_true(client):
    data = client.get("/readiness").json()
    assert data["backend_ready"] is True


def test_final_backend_ready_true(client):
    data = client.get("/readiness").json()
    assert data["final_backend_ready"] is True


def test_release_ready_true(client):
    data = client.get("/readiness").json()
    assert data["release_ready"] is True


def test_setup_completed_true(client):
    data = client.get("/readiness").json()
    assert data["setup_completed"] is True


def test_update_required_false(client):
    data = client.get("/readiness").json()
    assert data["update_required"] is False


def test_preflight_passed_false_simulation_default(client):
    """preflight_passed=False: simulation default, live not requested."""
    data = client.get("/readiness").json()
    assert data["preflight_passed"] is False


# ── Blocked reason messages ───────────────────────────────────────────────────

def test_blocked_reason_messages_is_list(client):
    data = client.get("/readiness").json()
    assert isinstance(data["blocked_reason_messages"], list)


def test_blocked_reason_messages_not_empty_when_blocked(client):
    data = client.get("/readiness").json()
    assert len(data["blocked_reason_messages"]) > 0


def test_blocked_reason_includes_live_auth_message(client):
    data = client.get("/readiness").json()
    msgs = data["blocked_reason_messages"]
    assert any("yetkilendirilmedi" in m for m in msgs)


# ── Port and poll config ──────────────────────────────────────────────────────

def test_frontend_port_is_integer(client):
    data = client.get("/readiness").json()
    assert isinstance(data["frontend_port"], int)


def test_backend_port_is_integer(client):
    data = client.get("/readiness").json()
    assert isinstance(data["backend_port"], int)


def test_readiness_poll_interval_ms_positive(client):
    data = client.get("/readiness").json()
    assert data["readiness_poll_interval_ms"] > 0


# ── No secrets in response ────────────────────────────────────────────────────

def test_no_api_key_in_response(client):
    """Response must not contain any secret-like fields."""
    data = client.get("/readiness").json()
    forbidden_keys = {"api_key", "secret", "password", "token", "credential"}
    for key in data:
        assert key.lower() not in forbidden_keys, f"Secret-like field in response: {key}"
