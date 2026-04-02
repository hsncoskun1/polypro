import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

TRIGGER_URL = "/api/v1/discovery/trigger"


@pytest.fixture()
def client(tmp_path):
    os.environ["MARKET_STORE_PATH"] = str(tmp_path / "test_markets.db")
    with TestClient(app) as c:
        yield c
    os.environ.pop("MARKET_STORE_PATH", None)


def test_trigger_returns_200(client):
    response = client.post(TRIGGER_URL, json={})
    assert response.status_code == 200


def test_trigger_response_contains_summary_fields(client):
    response = client.post(TRIGGER_URL, json={})
    data = response.json()
    summary = data["summary"]
    assert "added_count" in summary
    assert "skipped_duplicate_count" in summary
    assert "skipped_invalid_count" in summary
    assert "total_seen" in summary


def test_trigger_source_name_in_response(client):
    response = client.post(TRIGGER_URL, json={"source_name": "test-source"})
    assert response.json()["source_name"] == "test-source"


def test_trigger_ran_at_in_response(client):
    response = client.post(TRIGGER_URL, json={})
    assert "ran_at" in response.json()
    assert response.json()["ran_at"] is not None


def test_trigger_empty_source_returns_zero_summary(client):
    response = client.post(TRIGGER_URL, json={"items": []})
    summary = response.json()["summary"]
    assert summary["added_count"] == 0
    assert summary["skipped_duplicate_count"] == 0
    assert summary["skipped_invalid_count"] == 0
    assert summary["total_seen"] == 0


def test_trigger_mixed_input_returns_correct_counts(client):
    items = [
        {"market_id": "m1", "title": "Valid Market", "timeframe": "1W"},
        {"market_id": "m1", "title": "Duplicate", "timeframe": "1W"},
        {"market_id": "m3", "title": "Bad Timeframe", "timeframe": "INVALID"},
    ]
    response = client.post(TRIGGER_URL, json={"items": items, "source_name": "mixed"})
    assert response.status_code == 200
    summary = response.json()["summary"]
    assert summary["added_count"] == 1
    assert summary["skipped_duplicate_count"] == 1
    assert summary["skipped_invalid_count"] == 1
    assert summary["total_seen"] == 3
