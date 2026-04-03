"""Tests for auth_service — v1.0.6 (bcrypt, session TTL, reset token expiry)."""
import pytest
from datetime import datetime, timedelta, timezone

from app.domain.auth.auth_service import (
    SESSION_TTL_HOURS,
    RESET_TOKEN_TTL_MINUTES,
    create_user,
    hash_password,
    is_session_valid,
    login,
    logout,
    request_password_reset,
    reset_password,
    verify_password,
)
from app.domain.auth.user import User
from app.domain.auth.user_role import UserRole


def make_user(password: str = "secret123") -> User:
    return create_user("test@example.com", password)


class TestBcryptHashing:
    def test_hash_password_returns_bcrypt_hash(self):
        h = hash_password("secret")
        assert h.startswith("$2b$") or h.startswith("$2a$")

    def test_verify_password_correct(self):
        h = hash_password("secret")
        assert verify_password("secret", h) is True

    def test_verify_password_wrong(self):
        h = hash_password("secret")
        assert verify_password("wrong", h) is False

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt uses random salt — hashes must differ."""
        h1 = hash_password("secret")
        h2 = hash_password("secret")
        assert h1 != h2

    def test_hash_is_not_sha256(self):
        """SHA-256 hex is 64 chars, bcrypt starts with $2."""
        h = hash_password("secret")
        assert not (len(h) == 64 and all(c in "0123456789abcdef" for c in h))


class TestLogin:
    def test_login_success_returns_token(self):
        user = make_user("correct")
        token = login(user, "correct")
        assert token is not None
        assert len(token) == 64

    def test_login_sets_session_timestamps(self):
        user = make_user()
        login(user, "secret123")
        assert user.session_created_at is not None
        assert user.session_expires_at is not None
        delta = user.session_expires_at - user.session_created_at
        assert abs(delta.total_seconds() - SESSION_TTL_HOURS * 3600) < 5

    def test_login_wrong_password_returns_none(self):
        user = make_user()
        assert login(user, "wrong") is None

    def test_login_inactive_user_returns_none(self):
        user = make_user()
        user.is_active = False
        assert login(user, "secret123") is None


class TestSessionValidity:
    def test_valid_session_returns_true(self):
        user = make_user()
        login(user, "secret123")
        assert is_session_valid(user) is True

    def test_no_session_token_returns_false(self):
        user = make_user()
        assert is_session_valid(user) is False

    def test_expired_session_returns_false(self):
        user = make_user()
        login(user, "secret123")
        # Backdate expiry to past
        user.session_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        assert is_session_valid(user) is False

    def test_logout_clears_session(self):
        user = make_user()
        login(user, "secret123")
        logout(user)
        assert user.session_token is None
        assert user.session_expires_at is None
        assert is_session_valid(user) is False


class TestPasswordReset:
    def test_request_reset_sets_token_and_expiry(self):
        user = make_user()
        token = request_password_reset(user)
        assert token is not None
        assert user.password_reset_token == token
        assert user.password_reset_expires_at is not None
        delta = user.password_reset_expires_at - user.password_reset_requested_at
        assert abs(delta.total_seconds() - RESET_TOKEN_TTL_MINUTES * 60) < 5

    def test_reset_password_success(self):
        user = make_user("old")
        token = request_password_reset(user)
        result = reset_password(user, token, "new_password")
        assert result is True
        assert verify_password("new_password", user.password_hash)

    def test_reset_clears_token_single_use(self):
        user = make_user()
        token = request_password_reset(user)
        reset_password(user, token, "newpass")
        # Second use must fail
        assert reset_password(user, token, "anotherpass") is False

    def test_reset_wrong_token_fails(self):
        user = make_user()
        request_password_reset(user)
        assert reset_password(user, "wrong_token", "newpass") is False

    def test_reset_expired_token_fails(self):
        user = make_user()
        token = request_password_reset(user)
        # Backdate expiry
        user.password_reset_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        assert reset_password(user, token, "newpass") is False

    def test_reset_clears_session(self):
        user = make_user()
        login(user, "secret123")
        token = request_password_reset(user)
        reset_password(user, token, "newpass")
        assert user.session_token is None


class TestCreateUser:
    def test_create_user_sets_correct_role(self):
        user = create_user("admin@example.com", "pass", UserRole.admin)
        assert user.role == UserRole.admin

    def test_create_user_default_role_is_user(self):
        user = create_user("user@example.com", "pass")
        assert user.role == UserRole.user

    def test_create_user_password_is_bcrypt(self):
        user = create_user("u@e.com", "pass")
        assert user.password_hash.startswith("$2b$") or user.password_hash.startswith("$2a$")
