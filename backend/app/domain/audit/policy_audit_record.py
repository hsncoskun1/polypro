"""PolicyAuditRecord domain model — v1.1.2.

Records every admin entitlement/policy change with actor, target, before/after snapshot.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class PolicyAuditRecord:
    """Immutable audit record for an admin policy/entitlement change.

    audit_id      : unique record identifier (UUID or similar)
    actor_id      : user_id of the admin who made the change
    target_user_id: user_id whose entitlement was changed
    action        : short action label, e.g. 'update_entitlement'
    snapshot_before: dict of entitlement state before change (may be empty on first save)
    snapshot_after : dict of entitlement state after change
    changed_at    : UTC timestamp of the change
    """
    audit_id: str
    actor_id: str
    target_user_id: str
    action: str
    snapshot_before: Dict[str, Any]
    snapshot_after: Dict[str, Any]
    changed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def changed_fields(self) -> list[str]:
        """Return list of field names that differ between before and after."""
        before = self.snapshot_before
        after = self.snapshot_after
        all_keys = set(before.keys()) | set(after.keys())
        return sorted(k for k in all_keys if before.get(k) != after.get(k))
