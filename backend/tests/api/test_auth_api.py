"""Tests for auth API routes — v1.0.5."""
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
def registered_user(client):
    """Register a user via the store on app.state (set up by TestClient lifespan)."""
    user = auth_service.create_user("user@example.com", "password123")
    app.state.auth_store.save_user(user)
    return user


def test_login_success(client, registered_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "password123",
    })
    assert res.status_code == 200
    data = res.json()
    assert "session_token" in data
    assert data["email"] == "user@example.com"
    assert data["role"] == "user"


def test_login_wrong_password_returns_401(client, registered_user):
    res = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "wrongpass",
    })
    assert res.status_code == 401


def test_login_unknown_email_returns_401(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "any",
    })
    assert res.status_code == 401


def test_logout_success(client, registered_user):
    # First login to get a token
    res = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "password123",
    })
    token = res.json()["session_token"]
    # Logout
    res2 = client.post("/api/v1/auth/logout", json={"session_token": token})
    assert res2.status_code == 204
    # Token should be cleared
    user = app.state.auth_store.get_user_by_email("user@example.com")
    assert user.session_token is None


def test_forgot_password_returns_reset_token(client, registered_user):
    res = client.post("/api/v1/auth/forgot-password", json={"email": "user@example.com"})
    assert res.status_code == 200
    data = res.json()
    assert "reset_token" in data
    assert len(data["reset_token"]) > 10


def test_reset_password_success(client, registered_user):
    # Request reset
    res = client.post("/api/v1/auth/forgot-password", json={"email": "user@example.com"})
    reset_token = res.json()["reset_token"]
    # Reset password
    res2 = client.post("/api/v1/auth/reset-password", json={
        "email": "user@example.com",
        "reset_token": reset_token,
        "new_password": "newpass456",
    })
    assert res2.status_code == 204
    # New password works
    res3 = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "newpass456",
    })
    assert res3.status_code == 200


def test_reset_password_wrong_token_returns_400(client, registered_user):
    res = client.post("/api/v1/auth/reset-password", json={
        "email": "user@example.com",
        "reset_token": "badtoken",
        "new_password": "newpass",
    })
    assert res.status_code == 400
