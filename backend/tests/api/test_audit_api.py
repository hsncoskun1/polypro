"""Tests for policy audit trail API — v1.1.2."""
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.domain.auth import auth_service
from app.domain.auth.user_role import UserRole


@pytest.fixture()
def client(tmp_path):
    db_path = str(tmp_path / "test_auth.db")
    os.environ["AUTH_DB_PATH"] = db_path
    with TestClient(app) as c:
        yield c
    os.environ.pop("AUTH_DB_PATH", None)


@pytest.fixture()
def admin_token(client):
    admin = auth_service.create_user("admin@example.com", "adminpass", role=UserRole.admin)
    app.state.auth_store.save_user(admin)
    res = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "adminpass"})
    return res.json()["session_token"]


@pytest.fixture()
def user_token(client):
    user = auth_service.create_user("user@example.com", "userpass")
    app.state.auth_store.save_user(user)
    res = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "userpass"})
    return res.json()["session_token"], res.json()["user_id"]


@pytest.fixture()
def admin_and_user(client, admin_token, user_token):
    token, user_id = user_token
    return admin_token, token, user_id


def _update_entitlement(client, admin_token, user_id, **overrides):
    payload = {
        "license_status": "active",
        "expires_at": None,
        "trading_enabled": True,
        "allowed_features": [],
        "visible_panels": [],
        "visible_rules": [],
        "editable_rules": [],
        "blocked_reason_messages": [],
        **overrides,
    }
    return client.put(
        f"/api/v1/admin/users/{user_id}/entitlement",
        json=payload,
        headers={"X-Session-Token": admin_token},
    )


# ── Audit record creation on entitlement update ───────────────────────────────

def test_audit_record_created_on_entitlement_update(client, admin_and_user):
    admin_token, _, user_id = admin_and_user
    _update_entitlement(client, admin_token, user_id, trading_enabled=True)
    res = client.get(
        f"/api/v1/admin/users/{user_id}/audit",
        headers={"X-Session-Token": admin_token},
    )
    assert res.status_code == 200
    records = res.json()
    assert len(records) == 1
    assert records[0]["action"] == "update_entitlement"
    assert records[0]["target_user_id"] == user_id


def test_audit_record_contains_actor_id(client, admin_and_user):
    admin_token, _, user_id = admin_and_user
    _update_entitlement(client, admin_token, user_id)
    res = client.get(
        f"/api/v1/admin/users/{user_id}/audit",
        headers={"X-Session-Token": admin_token},
    )
    record = res.json()[0]
    assert record["actor_id"] != ""
    assert record["actor_id"] != user_id  # actor is admin, not target


def test_audit_record_snapshot_after_matches_saved(client, admin_and_user):
    admin_token, _, user_id = admin_and_user
    _update_entitlement(client, admin_token, user_id, trading_enabled=True, license_status="active")
    res = client.get(
        f"/api/v1/admin/users/{user_id}/audit",
        headers={"X-Session-Token": admin_token},
    )
    record = res.json()[0]
    assert record["snapshot_after"]["trading_enabled"] is True
    assert record["snapshot_after"]["license_status"] == "active"


def test_audit_changed_fields_populated(client, admin_and_user):
    admin_token, _, user_id = admin_and_user
    # First save
    _update_entitlement(client, admin_token, user_id, trading_enabled=False, license_status="inactive")
    # Second save — change trading_enabled
    _update_entitlement(client, admin_token, user_id, trading_enabled=True, license_status="active")
    res = client.get(
        f"/api/v1/admin/users/{user_id}/audit",
        headers={"X-Session-Token": admin_token},
    )
    records = res.json()
    assert len(records) == 2
    # Most recent first — second change should have changed_fields
    second = records[0]
    assert "trading_enabled" in second["changed_fields"] or "license_status" in second["changed_fields"]


def test_multiple_updates_produce_multiple_records(client, admin_and_user):
    admin_token, _, user_id = admin_and_user
    _update_entitlement(client, admin_token, user_id)
    _update_entitlement(client, admin_token, user_id, trading_enabled=False)
    res = client.get(
        f"/api/v1/admin/users/{user_id}/audit",
        headers={"X-Session-Token": admin_token},
    )
    assert len(res.json()) == 2


# ── Access control ────────────────────────────────────────────────────────────

def test_audit_endpoint_requires_admin(client, admin_and_user):
    admin_token, user_token, user_id = admin_and_user
    _update_entitlement(client, admin_token, user_id)
    # Non-admin tries to access audit log
    res = client.get(
        f"/api/v1/admin/users/{user_id}/audit",
        headers={"X-Session-Token": user_token},
    )
    assert res.status_code == 403


def test_audit_endpoint_requires_auth(client, admin_and_user):
    admin_token, _, user_id = admin_and_user
    _update_entitlement(client, admin_token, user_id)
    res = client.get(f"/api/v1/admin/users/{user_id}/audit")
    assert res.status_code == 401


def test_audit_empty_for_user_with_no_updates(client, admin_and_user):
    admin_token, _, user_id = admin_and_user
    res = client.get(
        f"/api/v1/admin/users/{user_id}/audit",
        headers={"X-Session-Token": admin_token},
    )
    assert res.status_code == 200
    assert res.json() == []
