import os
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.domain.markets.discovery import DiscoverySummary
from app.services.discovery import DiscoveryResult

TRIGGER_URL = "/api/v1/discovery/trigger"
_PATCH_TARGET = "app.api.discovery.run_polymarket_fetch_to_discovery"
_CLIENT_PATCH = "app.api.discovery.PolymarketClient"
_CONFIG_URL_PATCH = "app.api.discovery.POLYMARKET_URL"

_DEFAULT_TOKEN = "dev-token"
_AUTH_HEADER = {"Authorization": f"Bearer {_DEFAULT_TOKEN}"}

_RAN_AT = datetime(2026, 4, 2, 12, 0, 0, tzinfo=timezone.utc)


def _make_result(added=0, skipped_dup=0, skipped_inv=0, source_name="polymarket"):
    return DiscoveryResult(
        summary=DiscoverySummary(
            added_count=added,
            skipped_duplicate_count=skipped_dup,
            skipped_invalid_count=skipped_inv,
            total_seen=added + skipped_dup + skipped_inv,
        ),
        source_name=source_name,
        ran_at=_RAN_AT,
    )


@pytest.fixture()
def client(tmp_path):
    os.environ["MARKET_STORE_PATH"] = str(tmp_path / "test_markets.db")
    os.environ["TRIGGER_AUTH_TOKEN"] = _DEFAULT_TOKEN
    with TestClient(app) as c:
        yield c
    os.environ.pop("MARKET_STORE_PATH", None)
    os.environ.pop("TRIGGER_AUTH_TOKEN", None)


@pytest.fixture()
def no_auth_config_client(tmp_path):
    os.environ["MARKET_STORE_PATH"] = str(tmp_path / "test_markets.db")
    os.environ.pop("TRIGGER_AUTH_TOKEN", None)
    with TestClient(app) as c:
        yield c
    os.environ.pop("MARKET_STORE_PATH", None)


# ── Happy path ────────────────────────────────────────────────────────────────

def test_trigger_returns_200(client):
    with patch(_PATCH_TARGET, return_value=_make_result()):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    assert response.status_code == 200


def test_trigger_response_contains_summary_fields(client):
    with patch(_PATCH_TARGET, return_value=_make_result()):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    summary = response.json()["summary"]
    assert "added_count" in summary
    assert "skipped_duplicate_count" in summary
    assert "skipped_invalid_count" in summary
    assert "total_seen" in summary


def test_trigger_empty_fetch_returns_zero_summary(client):
    with patch(_PATCH_TARGET, return_value=_make_result()):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    summary = response.json()["summary"]
    assert summary["added_count"] == 0
    assert summary["skipped_duplicate_count"] == 0
    assert summary["skipped_invalid_count"] == 0
    assert summary["total_seen"] == 0


def test_trigger_source_name_preserved_in_response(client):
    with patch(_PATCH_TARGET, return_value=_make_result(source_name="test-source")):
        response = client.post(
            TRIGGER_URL, json={"source_name": "test-source"}, headers=_AUTH_HEADER
        )
    assert response.json()["source_name"] == "test-source"


def test_trigger_default_source_name_is_polymarket(client):
    with patch(_PATCH_TARGET, return_value=_make_result(source_name="polymarket")) as mock_fn:
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    _, kwargs = mock_fn.call_args
    assert kwargs.get("source_name") == "polymarket"
    assert response.json()["source_name"] == "polymarket"


def test_trigger_ran_at_in_response(client):
    with patch(_PATCH_TARGET, return_value=_make_result()):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    data = response.json()
    assert "ran_at" in data
    assert data["ran_at"] is not None


def test_trigger_ran_at_is_parseable_iso_format(client):
    with patch(_PATCH_TARGET, return_value=_make_result()):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    ran_at = response.json()["ran_at"]
    parsed = datetime.fromisoformat(ran_at)
    assert parsed.tzinfo is not None


def test_trigger_mixed_result_reflected_in_summary(client):
    with patch(_PATCH_TARGET, return_value=_make_result(added=2, skipped_dup=1, skipped_inv=1)):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    summary = response.json()["summary"]
    assert summary["added_count"] == 2
    assert summary["skipped_duplicate_count"] == 1
    assert summary["skipped_invalid_count"] == 1
    assert summary["total_seen"] == 4


# ── Error propagation ─────────────────────────────────────────────────────────

def test_client_error_returns_502(client):
    from app.clients.polymarket import PolymarketClientError
    with patch(_PATCH_TARGET, side_effect=PolymarketClientError("fetch failed")):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    assert response.status_code == 502


def test_timeframe_mapping_error_returns_422(client):
    from app.clients.timeframe_mapping import TimeframeMappingError
    with patch(_PATCH_TARGET, side_effect=TimeframeMappingError("bad date")):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    assert response.status_code == 422


def test_client_payload_mapping_error_returns_422(client):
    from app.clients.polymarket_mapping import ClientPayloadMappingError
    with patch(_PATCH_TARGET, side_effect=ClientPayloadMappingError("missing field")):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    assert response.status_code == 422


# ── Validation (422) ──────────────────────────────────────────────────────────

def test_trigger_empty_source_name_returns_422(client):
    response = client.post(TRIGGER_URL, json={"source_name": ""}, headers=_AUTH_HEADER)
    assert response.status_code == 422


def test_trigger_invalid_timeout_returns_422(client):
    response = client.post(TRIGGER_URL, json={"timeout": -1}, headers=_AUTH_HEADER)
    assert response.status_code == 422


def test_trigger_zero_timeout_returns_422(client):
    response = client.post(TRIGGER_URL, json={"timeout": 0}, headers=_AUTH_HEADER)
    assert response.status_code == 422


def test_trigger_timeout_above_max_returns_422(client):
    response = client.post(TRIGGER_URL, json={"timeout": 120}, headers=_AUTH_HEADER)
    assert response.status_code == 422


# ── URL / timeout wiring ──────────────────────────────────────────────────────

def test_trigger_uses_config_url_when_body_url_is_null(client):
    with patch(_PATCH_TARGET, return_value=_make_result()), \
         patch(_CLIENT_PATCH) as mock_client_cls, \
         patch(_CONFIG_URL_PATCH, "https://test-polymarket.example.com/markets"):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    call_args = mock_client_cls.call_args
    assert call_args[0][0] == "https://test-polymarket.example.com/markets"
    assert response.status_code == 200


def test_trigger_uses_body_url_when_provided(client):
    with patch(_PATCH_TARGET, return_value=_make_result()), \
         patch(_CLIENT_PATCH) as mock_client_cls:
        response = client.post(
            TRIGGER_URL,
            json={"url": "https://override.example.com/markets"},
            headers=_AUTH_HEADER,
        )
    call_args = mock_client_cls.call_args
    assert call_args[0][0] == "https://override.example.com/markets"
    assert response.status_code == 200


def test_trigger_passes_timeout_to_client(client):
    with patch(_PATCH_TARGET, return_value=_make_result()), \
         patch(_CLIENT_PATCH) as mock_client_cls:
        response = client.post(TRIGGER_URL, json={"timeout": 5.0}, headers=_AUTH_HEADER)
    call_kwargs = mock_client_cls.call_args[1]
    assert call_kwargs.get("timeout") == 5.0
    assert response.status_code == 200


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_trigger_auth_not_configured_returns_500(no_auth_config_client):
    response = no_auth_config_client.post(TRIGGER_URL, json={})
    assert response.status_code == 500


def test_trigger_missing_auth_header_returns_401(client):
    response = client.post(TRIGGER_URL, json={})
    assert response.status_code == 401


def test_trigger_wrong_token_returns_401(client):
    response = client.post(
        TRIGGER_URL, json={}, headers={"Authorization": "Bearer wrong-token"}
    )
    assert response.status_code == 401


def test_trigger_correct_token_returns_200(client):
    with patch(_PATCH_TARGET, return_value=_make_result()):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    assert response.status_code == 200


def test_trigger_correct_token_response_shape_intact(client):
    with patch(_PATCH_TARGET, return_value=_make_result(added=1)):
        response = client.post(TRIGGER_URL, json={}, headers=_AUTH_HEADER)
    data = response.json()
    assert "summary" in data
    assert "source_name" in data
    assert "ran_at" in data
