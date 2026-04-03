"""Tests for user entitlement API route — v1.0.5."""
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.domain.auth import auth_service
from app.domain.auth.user_role import UserRole
from app.domain.entitlement.entitlement import Entitlement
from app.domain.entitlement.license_status import LicenseStatus


@pytest.fixture()
def client(tmp_path):
    db_path = str(tmp_path / "test_user_ent.db")
    os.environ["AUTH_DB_PATH"] = db_path
    with TestClient(app) as c:
        yield c
    os.environ.pop("AUTH_DB_PATH", None)


@pytest.fixture()
def regular_user(client):
    user = auth_service.create_user("user@example.com", "pass123", UserRole.user)
    app.state.auth_store.save_user(user)
    return user


@pytest.fixture()
def user_token(client, regular_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "pass123",
    })
    return res.json()["session_token"]


def test_get_entitlement_requires_session_token(client):
    res = client.get("/api/v1/user/entitlement")
    assert res.status_code == 401


def test_get_entitlement_returns_default_when_none(client, user_token):
    # No entitlement stored for user
    res = client.get(
        "/api/v1/user/entitlement",
        headers={"X-Session-Token": user_token},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["trading_enabled"] is False
    assert data["license_status"] == "inactive"
    assert "Trading disabled: license not active or expired." in data["blocked_reason_messages"]


def test_get_entitlement_active_license(client, user_token, regular_user):
    from datetime import datetime, timezone, timedelta
    future = datetime.now(timezone.utc) + timedelta(days=30)
    ent = Entitlement(
        user_id=regular_user.user_id,
        license_status=LicenseStatus.active,
        expires_at=future,
        trading_enabled=True,
        allowed_features=["feature_x"],
    )
    app.state.auth_store.save_entitlement(ent)
    res = client.get(
        "/api/v1/user/entitlement",
        headers={"X-Session-Token": user_token},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["trading_enabled"] is True
    assert data["license_status"] == "active"
    assert "feature_x" in data["allowed_features"]
