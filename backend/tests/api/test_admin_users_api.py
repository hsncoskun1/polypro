"""Tests for admin users API routes — v1.0.5."""
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
    db_path = str(tmp_path / "test_admin.db")
    os.environ["AUTH_DB_PATH"] = db_path
    with TestClient(app) as c:
        yield c
    os.environ.pop("AUTH_DB_PATH", None)


@pytest.fixture()
def admin_user(client):
    user = auth_service.create_user("admin@example.com", "adminpass", UserRole.admin)
    app.state.auth_store.save_user(user)
    return user


@pytest.fixture()
def admin_token(client, admin_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpass",
    })
    return res.json()["session_token"]


@pytest.fixture()
def regular_user(client):
    user = auth_service.create_user("user@example.com", "userpass", UserRole.user)
    app.state.auth_store.save_user(user)
    return user


@pytest.fixture()
def user_token(client, regular_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "userpass",
    })
    return res.json()["session_token"]


def test_list_users_requires_admin(client, user_token):
    res = client.get("/api/v1/admin/users", headers={"X-Session-Token": user_token})
    assert res.status_code == 403


def test_list_users_as_admin_returns_users(client, admin_token, regular_user, admin_user):
    res = client.get("/api/v1/admin/users", headers={"X-Session-Token": admin_token})
    assert res.status_code == 200
    data = res.json()
    emails = [u["email"] for u in data]
    assert "admin@example.com" in emails
    assert "user@example.com" in emails


def test_admin_summary_returns_counts(client, admin_token):
    res = client.get("/api/v1/admin/summary", headers={"X-Session-Token": admin_token})
    assert res.status_code == 200
    data = res.json()
    assert "online_user_count" in data
    assert "total_user_count" in data
    assert data["total_user_count"] >= 1


def test_update_entitlement_sets_trading_enabled(client, admin_token, regular_user):
    from datetime import datetime, timezone, timedelta
    future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    res = client.put(
        f"/api/v1/admin/users/{regular_user.user_id}/entitlement",
        headers={"X-Session-Token": admin_token},
        json={
            "license_status": "active",
            "expires_at": future,
            "trading_enabled": True,
            "allowed_features": [],
            "visible_panels": [],
            "visible_rules": [],
            "editable_rules": [],
            "blocked_reason_messages": [],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["trading_enabled"] is True
    assert data["license_status"] == "active"


def test_update_entitlement_inactive_license_forces_trading_disabled(client, admin_token, regular_user):
    res = client.put(
        f"/api/v1/admin/users/{regular_user.user_id}/entitlement",
        headers={"X-Session-Token": admin_token},
        json={
            "license_status": "inactive",
            "expires_at": None,
            "trading_enabled": True,  # Requested but should be forced False
            "allowed_features": [],
            "visible_panels": [],
            "visible_rules": [],
            "editable_rules": [],
            "blocked_reason_messages": [],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["trading_enabled"] is False


def test_get_user_entitlement_not_found_404(client, admin_token):
    res = client.get(
        "/api/v1/admin/users/nonexistent-user-id/entitlement",
        headers={"X-Session-Token": admin_token},
    )
    assert res.status_code == 404
