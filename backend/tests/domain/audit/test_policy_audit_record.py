"""Tests for PolicyAuditRecord domain model — v1.1.2."""
from datetime import datetime, timezone
from app.domain.audit.policy_audit_record import PolicyAuditRecord


def make_record(**kwargs) -> PolicyAuditRecord:
    defaults = dict(
        audit_id="audit-001",
        actor_id="admin-1",
        target_user_id="user-1",
        action="update_entitlement",
        snapshot_before={},
        snapshot_after={},
        changed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    defaults.update(kwargs)
    return PolicyAuditRecord(**defaults)


def test_policy_audit_record_stores_fields():
    r = make_record()
    assert r.audit_id == "audit-001"
    assert r.actor_id == "admin-1"
    assert r.target_user_id == "user-1"
    assert r.action == "update_entitlement"


def test_changed_fields_detects_differences():
    r = make_record(
        snapshot_before={"trading_enabled": False, "license_status": "inactive"},
        snapshot_after={"trading_enabled": True, "license_status": "inactive"},
    )
    assert r.changed_fields() == ["trading_enabled"]


def test_changed_fields_multiple():
    r = make_record(
        snapshot_before={"trading_enabled": False, "license_status": "inactive"},
        snapshot_after={"trading_enabled": True, "license_status": "active"},
    )
    assert set(r.changed_fields()) == {"trading_enabled", "license_status"}


def test_changed_fields_empty_when_identical():
    snap = {"trading_enabled": True, "license_status": "active"}
    r = make_record(snapshot_before=snap, snapshot_after=dict(snap))
    assert r.changed_fields() == []


def test_changed_fields_new_key_in_after():
    r = make_record(
        snapshot_before={},
        snapshot_after={"trading_enabled": True},
    )
    assert r.changed_fields() == ["trading_enabled"]


def test_default_changed_at_is_utc():
    r = PolicyAuditRecord(
        audit_id="x", actor_id="a", target_user_id="u",
        action="test", snapshot_before={}, snapshot_after={},
    )
    assert r.changed_at.tzinfo is not None
