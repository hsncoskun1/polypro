"""Tests for entitlement_service — v1.0.5."""
import pytest
from datetime import datetime, timezone, timedelta

from app.domain.entitlement.entitlement import Entitlement
from app.domain.entitlement.entitlement_service import (
    compute_trading_enabled,
    apply_license_enforcement,
    is_trading_enabled,
)
from app.domain.entitlement.license_status import LicenseStatus


def _active_ent(expires_at=None) -> Entitlement:
    return Entitlement(
        user_id="u1",
        license_status=LicenseStatus.active,
        expires_at=expires_at,
        trading_enabled=False,
    )


def _inactive_ent() -> Entitlement:
    return Entitlement(
        user_id="u1",
        license_status=LicenseStatus.inactive,
        trading_enabled=False,
    )


def test_active_license_not_expired_trading_enabled():
    future = datetime.now(timezone.utc) + timedelta(days=30)
    ent = _active_ent(expires_at=future)
    assert compute_trading_enabled(ent) is True


def test_inactive_license_trading_disabled():
    ent = _inactive_ent()
    assert compute_trading_enabled(ent) is False


def test_expired_license_trading_disabled():
    ent = Entitlement(
        user_id="u1",
        license_status=LicenseStatus.expired,
        trading_enabled=False,
    )
    assert compute_trading_enabled(ent) is False


def test_expired_datetime_trading_disabled():
    past = datetime.now(timezone.utc) - timedelta(days=1)
    ent = _active_ent(expires_at=past)
    assert compute_trading_enabled(ent) is False


def test_none_entitlement_trading_disabled():
    assert is_trading_enabled(None) is False


def test_apply_enforcement_adds_blocked_message_when_disabled():
    ent = _inactive_ent()
    ent = apply_license_enforcement(ent)
    assert ent.trading_enabled is False
    assert "Trading disabled: license not active or expired." in ent.blocked_reason_messages


def test_apply_enforcement_removes_blocked_message_when_enabled():
    future = datetime.now(timezone.utc) + timedelta(days=30)
    ent = _active_ent(expires_at=future)
    ent.blocked_reason_messages = ["Trading disabled: license not active or expired."]
    ent = apply_license_enforcement(ent)
    assert ent.trading_enabled is True
    assert "Trading disabled: license not active or expired." not in ent.blocked_reason_messages


def test_active_no_expiry_trading_enabled():
    ent = _active_ent(expires_at=None)
    assert compute_trading_enabled(ent) is True
