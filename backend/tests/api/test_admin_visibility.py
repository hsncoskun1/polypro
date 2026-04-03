"""Tests for admin visibility/entitlement enforcement — v1.0.7."""
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.domain.auth import auth_service
from app.domain.auth.user_role import UserRole


@pytest.fixture()
def client(tmp_path):
    db_path = str(tmp_path / "test_visibility.db")
    os.environ["AUTH_DB_PATH"] = db_path
    with TestClient(app) as c:
        yield c
    os.environ.pop("AUTH_DB_PATH", None)


@pytest.fixture()
def admin_user(client):
    user = auth_service.create_user("admin@test.com", "admin123", UserRole.admin)
    app.state.auth_store.save_user(user)
    return user


@pytest.fixture()
def admin_token(client, admin_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123",
    })
    return res.json()["session_token"]


@pytest.fixture()
def regular_user(client):
    user = auth_service.create_user("user@test.com", "user123", UserRole.user)
    app.state.auth_store.save_user(user)
    return user


@pytest.fixture()
def user_token(client, regular_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "user@test.com",
        "password": "user123",
    })
    return res.json()["session_token"]


def test_list_users_as_admin(client, admin_token, regular_user, admin_user):
    res = client.get("/api/v1/admin/users", headers={"X-Session-Token": admin_token})
    assert res.status_code == 200
    emails = [u["email"] for u in res.json()]
    assert "user@test.com" in emails


def test_list_users_no_token_returns_401(client):
    res = client.get("/api/v1/admin/users")
    assert res.status_code == 401


def test_admin_summary_returns_counts(client, admin_token):
    res = client.get("/api/v1/admin/summary", headers={"X-Session-Token": admin_token})
    assert res.status_code == 200
    data = res.json()
    assert "online_user_count" in data
    assert "total_user_count" in data


def test_update_entitlement_sets_visible_panels(client, admin_token, regular_user):
    payload = {
        "license_status": "active",
        "expires_at": None,
        "trading_enabled": True,
        "allowed_features": [],
        "visible_panels": ["dashboard", "positions"],
        "visible_rules": ["rule_a"],
        "editable_rules": [],
        "blocked_reason_messages": [],
    }
    res = client.put(
        f"/api/v1/admin/users/{regular_user.user_id}/entitlement",
        json=payload,
        headers={"X-Session-Token": admin_token},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["visible_panels"] == ["dashboard", "positions"]
    assert data["visible_rules"] == ["rule_a"]
    assert data["trading_enabled"] is True


def test_update_entitlement_inactive_license_disables_trading(client, admin_token, regular_user):
    payload = {
        "license_status": "inactive",
        "expires_at": None,
        "trading_enabled": True,  # should be overridden to False
        "allowed_features": [],
        "visible_panels": [],
        "visible_rules": [],
        "editable_rules": [],
        "blocked_reason_messages": [],
    }
    res = client.put(
        f"/api/v1/admin/users/{regular_user.user_id}/entitlement",
        json=payload,
        headers={"X-Session-Token": admin_token},
    )
    assert res.status_code == 200
    assert res.json()["trading_enabled"] is False


def test_non_admin_cannot_list_users(client, user_token):
    res = client.get("/api/v1/admin/users", headers={"X-Session-Token": user_token})
    assert res.status_code == 403
