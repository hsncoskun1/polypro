"""Tests for auth_service — v1.0.5."""
import pytest
from app.domain.auth import auth_service
from app.domain.auth.user import User
from app.domain.auth.user_role import UserRole


def _make_user(email: str = "test@example.com", password: str = "secret", active: bool = True) -> User:
    return auth_service.create_user(email, password)


# --- hash / verify ---

def test_hash_password_deterministic():
    h1 = auth_service.hash_password("mypassword")
    h2 = auth_service.hash_password("mypassword")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex


def test_verify_password_correct():
    hashed = auth_service.hash_password("correct")
    assert auth_service.verify_password("correct", hashed) is True


def test_verify_password_wrong():
    hashed = auth_service.hash_password("correct")
    assert auth_service.verify_password("wrong", hashed) is False


# --- login ---

def test_login_success_returns_token():
    user = _make_user(password="goodpass")
    token = auth_service.login(user, "goodpass")
    assert token is not None
    assert len(token) == 64  # token_hex(32)
    assert user.session_token == token
    assert user.last_login_at is not None


def test_login_wrong_password_returns_none():
    user = _make_user(password="goodpass")
    result = auth_service.login(user, "badpass")
    assert result is None
    assert user.session_token is None


def test_login_inactive_user_returns_none():
    user = _make_user(password="goodpass")
    user.is_active = False
    result = auth_service.login(user, "goodpass")
    assert result is None


# --- logout ---

def test_logout_clears_token():
    user = _make_user(password="pass")
    auth_service.login(user, "pass")
    assert user.session_token is not None
    auth_service.logout(user)
    assert user.session_token is None


# --- password reset ---

def test_request_password_reset_sets_token():
    user = _make_user()
    token = auth_service.request_password_reset(user)
    assert user.password_reset_token == token
    assert len(token) > 10


def test_reset_password_success():
    user = _make_user(password="oldpass")
    reset_token = auth_service.request_password_reset(user)
    auth_service.login(user, "oldpass")
    result = auth_service.reset_password(user, reset_token, "newpass")
    assert result is True
    assert user.password_reset_token is None
    assert user.session_token is None
    # New password works
    assert auth_service.verify_password("newpass", user.password_hash)


def test_reset_password_wrong_token_fails():
    user = _make_user(password="oldpass")
    auth_service.request_password_reset(user)
    result = auth_service.reset_password(user, "wrongtoken", "newpass")
    assert result is False
    # Password unchanged
    assert auth_service.verify_password("oldpass", user.password_hash)


# --- create_user ---

def test_create_user_sets_correct_fields():
    user = auth_service.create_user("alice@example.com", "pass123", UserRole.admin)
    assert user.email == "alice@example.com"
    assert user.role == UserRole.admin
    assert user.is_active is True
    assert user.session_token is None
    assert auth_service.verify_password("pass123", user.password_hash)
