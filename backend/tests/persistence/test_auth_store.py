"""Tests for AuthStore — v1.0.5."""
import pytest
from datetime import datetime, timezone
from app.domain.auth.user import User
from app.domain.auth.user_role import UserRole
from app.domain.entitlement.entitlement import Entitlement
from app.domain.entitlement.license_status import LicenseStatus
from app.persistence.auth_store import AuthStore


@pytest.fixture
def store(tmp_path):
    db_path = str(tmp_path / "test_auth.db")
    return AuthStore(db_path=db_path)


def _make_user(email: str = "test@example.com") -> User:
    return User(
        user_id="uid-1",
        email=email,
        password_hash="hash123",
        role=UserRole.user,
        is_active=True,
    )


def test_save_and_get_user_by_email(store):
    user = _make_user()
    store.save_user(user)
    result = store.get_user_by_email("test@example.com")
    assert result is not None
    assert result.user_id == "uid-1"
    assert result.email == "test@example.com"
    assert result.role == UserRole.user


def test_get_user_by_id(store):
    user = _make_user()
    store.save_user(user)
    result = store.get_user_by_id("uid-1")
    assert result is not None
    assert result.email == "test@example.com"


def test_get_user_by_session_token(store):
    user = _make_user()
    user.session_token = "tok-abc"
    store.save_user(user)
    result = store.get_user_by_session_token("tok-abc")
    assert result is not None
    assert result.user_id == "uid-1"


def test_list_users(store):
    u1 = _make_user("a@example.com")
    u1.user_id = "uid-a"
    u2 = _make_user("b@example.com")
    u2.user_id = "uid-b"
    store.save_user(u1)
    store.save_user(u2)
    users = store.list_users()
    assert len(users) == 2
    emails = {u.email for u in users}
    assert "a@example.com" in emails
    assert "b@example.com" in emails


def test_save_and_get_entitlement(store):
    ent = Entitlement(
        user_id="uid-1",
        license_status=LicenseStatus.active,
        trading_enabled=True,
        allowed_features=["feature_a"],
        visible_panels=["panel1"],
    )
    store.save_entitlement(ent)
    result = store.get_entitlement("uid-1")
    assert result is not None
    assert result.license_status == LicenseStatus.active
    assert result.trading_enabled is True
    assert "feature_a" in result.allowed_features
    assert "panel1" in result.visible_panels


def test_count_active_sessions(store):
    u1 = _make_user("a@example.com")
    u1.user_id = "uid-a"
    u1.session_token = "tok1"
    u2 = _make_user("b@example.com")
    u2.user_id = "uid-b"
    u2.session_token = None
    store.save_user(u1)
    store.save_user(u2)
    assert store.count_active_sessions() == 1


def test_update_user_clears_session_token(store):
    user = _make_user()
    user.session_token = "tok-abc"
    store.save_user(user)
    # Clear token via update
    user.session_token = None
    store.save_user(user)
    result = store.get_user_by_email("test@example.com")
    assert result is not None
    assert result.session_token is None
    # Count should be 0
    assert store.count_active_sessions() == 0
