"""Tests for AuthStore — v1.0.6 (session TTL, reset token expiry columns)."""
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.domain.auth.auth_service import create_user, login, request_password_reset
from app.domain.auth.user import User
from app.domain.auth.user_role import UserRole
from app.domain.entitlement.entitlement import Entitlement
from app.domain.entitlement.license_status import LicenseStatus
from app.persistence.auth_store import AuthStore


@pytest.fixture
def store(tmp_path):
    return AuthStore(db_path=str(tmp_path / "test_auth.db"))


def make_user(email: str = "a@b.com", password: str = "pass") -> User:
    return create_user(email, password)


class TestUserCRUD:
    def test_save_and_get_by_email(self, store):
        user = make_user()
        store.save_user(user)
        found = store.get_user_by_email(user.email)
        assert found is not None
        assert found.user_id == user.user_id

    def test_get_user_by_id(self, store):
        user = make_user()
        store.save_user(user)
        found = store.get_user_by_id(user.user_id)
        assert found is not None

    def test_get_user_by_session_token(self, store):
        user = make_user()
        login(user, "pass")
        store.save_user(user)
        found = store.get_user_by_session_token(user.session_token)
        assert found is not None

    def test_session_timestamps_persisted(self, store):
        user = make_user()
        login(user, "pass")
        store.save_user(user)
        found = store.get_user_by_id(user.user_id)
        assert found.session_created_at is not None
        assert found.session_expires_at is not None

    def test_reset_token_timestamps_persisted(self, store):
        user = make_user()
        store.save_user(user)
        request_password_reset(user)
        store.save_user(user)
        found = store.get_user_by_id(user.user_id)
        assert found.password_reset_token is not None
        assert found.password_reset_requested_at is not None
        assert found.password_reset_expires_at is not None

    def test_list_users(self, store):
        store.save_user(make_user("a@a.com"))
        store.save_user(make_user("b@b.com"))
        assert len(store.list_users()) == 2

    def test_count_active_sessions(self, store):
        user = make_user()
        login(user, "pass")
        store.save_user(user)
        assert store.count_active_sessions() == 1


class TestEntitlementCRUD:
    def test_save_and_get_entitlement(self, store):
        ent = Entitlement(
            user_id="u1",
            license_status=LicenseStatus.active,
            trading_enabled=True,
        )
        store.save_entitlement(ent)
        found = store.get_entitlement("u1")
        assert found is not None
        assert found.trading_enabled is True
        assert found.license_status == LicenseStatus.active
