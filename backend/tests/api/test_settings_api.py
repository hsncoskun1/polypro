"""Tests for GET /settings — v0.9.0"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ENDPOINT = "/settings"


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
        "api_key_configured", "api_secret_configured", "api_passphrase_configured",
        "relayer_api_configured", "wallet_address_configured",
        "funder_address_configured", "private_key_configured",
        "explicit_live_enable", "live_test_gate_enabled", "live_test_gate_passed",
        "client_mode", "minimum_order_size", "selected_event", "selected_market",
        "release_ready", "live_applied_testing_ready",
        "blocked_reason_messages", "masked_secret_fields",
    ]
    for field in required:
        assert field in data, f"Missing field: {field}"


# --- Credential status defaults ---

def test_api_key_not_configured(data):
    assert data["api_key_configured"] is False


def test_api_secret_not_configured(data):
    assert data["api_secret_configured"] is False


def test_api_passphrase_not_configured(data):
    assert data["api_passphrase_configured"] is False


def test_relayer_api_not_configured(data):
    assert data["relayer_api_configured"] is False


def test_wallet_address_not_configured(data):
    assert data["wallet_address_configured"] is False


def test_funder_address_not_configured(data):
    assert data["funder_address_configured"] is False


def test_private_key_not_configured(data):
    assert data["private_key_configured"] is False


# --- Live configuration defaults ---

def test_explicit_live_enable_false(data):
    assert data["explicit_live_enable"] is False


def test_live_test_gate_enabled_false(data):
    assert data["live_test_gate_enabled"] is False


def test_live_test_gate_passed_false(data):
    assert data["live_test_gate_passed"] is False


# --- Trading configuration defaults ---

def test_client_mode_simulation_mock(data):
    assert data["client_mode"] == "simulation_mock"


def test_minimum_order_size_zero(data):
    assert data["minimum_order_size"] == 0.0


def test_selected_event_empty(data):
    assert data["selected_event"] == ""


def test_selected_market_empty(data):
    assert data["selected_market"] == ""


# --- Release gate invariants ---

def test_release_ready_true(data):
    assert data["release_ready"] is True


def test_live_applied_testing_ready_always_false(data):
    assert data["live_applied_testing_ready"] is False


def test_blocked_reason_messages_not_empty(data):
    assert isinstance(data["blocked_reason_messages"], list)
    assert len(data["blocked_reason_messages"]) > 0


def test_masked_secret_fields_empty(data):
    assert data["masked_secret_fields"] == []


# --- Security ---

def test_no_plaintext_credential_values(data):
    """No credential values should appear — only configured flags."""
    secret_keys = ["api_key", "api_secret", "api_passphrase", "relayer_api",
                   "wallet_address", "funder_address", "private_key"]
    for key in secret_keys:
        # The field should end with '_configured', not be a raw value
        assert key + "_configured" in data
        # The raw key without suffix should NOT be present
        assert key not in data, f"Raw credential field exposed: {key}"


def test_no_secret_string_values(data):
    """Only allowed string fields may have non-empty values."""
    allowed_string_fields = {"client_mode", "selected_event", "selected_market"}
    for field, value in data.items():
        if isinstance(value, str) and len(value) > 0:
            assert field in allowed_string_fields, \
                f"Unexpected non-empty string field: {field}={value}"
