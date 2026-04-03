"""Tests for PolicyAuditRecord persistence in AuthStore — v1.1.2."""
import os
import pytest
from datetime import datetime, timezone
from app.persistence.auth_store import AuthStore
from app.domain.audit.policy_audit_record import PolicyAuditRecord


@pytest.fixture()
def store(tmp_path):
    return AuthStore(db_path=str(tmp_path / "test.db"))


def _record(audit_id: str, target: str = "user-1", actor: str = "admin-1") -> PolicyAuditRecord:
    return PolicyAuditRecord(
        audit_id=audit_id,
        actor_id=actor,
        target_user_id=target,
        action="update_entitlement",
        snapshot_before={"trading_enabled": False},
        snapshot_after={"trading_enabled": True},
        changed_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )


def test_save_and_retrieve_audit_record(store):
    r = _record("a1")
    store.save_policy_audit_record(r)
    records = store.get_policy_audit_records("user-1")
    assert len(records) == 1
    assert records[0].audit_id == "a1"
    assert records[0].actor_id == "admin-1"
    assert records[0].target_user_id == "user-1"
    assert records[0].action == "update_entitlement"


def test_snapshot_before_after_roundtrip(store):
    r = _record("a2")
    store.save_policy_audit_record(r)
    records = store.get_policy_audit_records("user-1")
    assert records[0].snapshot_before == {"trading_enabled": False}
    assert records[0].snapshot_after == {"trading_enabled": True}


def test_get_records_for_different_user_returns_empty(store):
    store.save_policy_audit_record(_record("a3", target="user-1"))
    assert store.get_policy_audit_records("user-2") == []


def test_multiple_records_returned_newest_first(store):
    import time
    r1 = PolicyAuditRecord(
        audit_id="old", actor_id="admin-1", target_user_id="user-1",
        action="update_entitlement", snapshot_before={}, snapshot_after={},
        changed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    r2 = PolicyAuditRecord(
        audit_id="new", actor_id="admin-1", target_user_id="user-1",
        action="update_entitlement", snapshot_before={}, snapshot_after={},
        changed_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    store.save_policy_audit_record(r1)
    store.save_policy_audit_record(r2)
    records = store.get_policy_audit_records("user-1")
    assert records[0].audit_id == "new"
    assert records[1].audit_id == "old"


def test_changed_at_roundtrip(store):
    r = _record("a4")
    store.save_policy_audit_record(r)
    records = store.get_policy_audit_records("user-1")
    assert records[0].changed_at == datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
