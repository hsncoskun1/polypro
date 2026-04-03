"""Admin user management API routes — v1.1.2 (policy audit trail)."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas.auth import (
    AdminEntitlementUpdateRequest,
    AdminSummaryResponse,
    AdminUserSummary,
    EntitlementResponse,
    PolicyAuditRecordResponse,
)
from app.domain.audit.policy_audit_record import PolicyAuditRecord
from app.domain.entitlement.entitlement import Entitlement
from app.domain.entitlement.entitlement_service import apply_license_enforcement
from app.domain.entitlement.license_status import LicenseStatus

router = APIRouter(prefix="/api/v1/admin", tags=["admin-users"])


def _get_auth_store(request: Request):
    return request.app.state.auth_store


def _require_admin(request: Request):
    """Check session token belongs to an admin user."""
    token = request.headers.get("X-Session-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Session token required")
    store = _get_auth_store(request)
    user = store.get_user_by_session_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session token")
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@router.get("/users", response_model=List[AdminUserSummary])
def list_users(request: Request):
    _require_admin(request)
    store = _get_auth_store(request)
    users = store.list_users()
    result = []
    for u in users:
        ent = store.get_entitlement(u.user_id)
        result.append(AdminUserSummary(
            user_id=u.user_id,
            email=u.email,
            role=u.role.value,
            is_active=u.is_active,
            last_login_at=u.last_login_at.isoformat() if u.last_login_at else None,
            license_status=ent.license_status.value if ent else None,
            trading_enabled=ent.trading_enabled if ent else False,
        ))
    return result


@router.get("/summary", response_model=AdminSummaryResponse)
def admin_summary(request: Request):
    _require_admin(request)
    store = _get_auth_store(request)
    online = store.count_active_sessions()
    total = len(store.list_users())
    return AdminSummaryResponse(
        online_user_count=online,
        total_user_count=total,
        active_bot_count=0,
        open_position_count=0,
        closed_position_count=0,
        blocked_trade_count=0,
        alert_count=0,
    )


@router.get("/users/{user_id}/entitlement", response_model=EntitlementResponse)
def get_user_entitlement(user_id: str, request: Request):
    _require_admin(request)
    store = _get_auth_store(request)
    ent = store.get_entitlement(user_id)
    if ent is None:
        raise HTTPException(status_code=404, detail="Entitlement not found")
    return _ent_to_response(ent)


@router.put("/users/{user_id}/entitlement", response_model=EntitlementResponse)
def update_user_entitlement(user_id: str, body: AdminEntitlementUpdateRequest, request: Request):
    admin = _require_admin(request)
    store = _get_auth_store(request)
    user = store.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    expires = None
    if body.expires_at:
        try:
            expires = datetime.fromisoformat(body.expires_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expires_at format")

    # Capture before snapshot
    existing = store.get_entitlement(user_id)
    snapshot_before = _ent_to_snapshot(existing)

    ent = Entitlement(
        user_id=user_id,
        license_status=LicenseStatus(body.license_status),
        expires_at=expires,
        trading_enabled=body.trading_enabled,
        allowed_features=body.allowed_features,
        visible_panels=body.visible_panels,
        visible_rules=body.visible_rules,
        editable_rules=body.editable_rules,
        blocked_reason_messages=body.blocked_reason_messages,
    )
    ent = apply_license_enforcement(ent)
    store.save_entitlement(ent)

    # Write audit record
    snapshot_after = _ent_to_snapshot(ent)
    audit_record = PolicyAuditRecord(
        audit_id=str(uuid.uuid4()),
        actor_id=admin.user_id,
        target_user_id=user_id,
        action="update_entitlement",
        snapshot_before=snapshot_before,
        snapshot_after=snapshot_after,
        changed_at=datetime.now(timezone.utc),
    )
    store.save_policy_audit_record(audit_record)

    return _ent_to_response(ent)


@router.get("/users/{user_id}/audit", response_model=List[PolicyAuditRecordResponse])
def get_user_audit_log(user_id: str, request: Request):
    """Return policy audit log for a user — admin only."""
    _require_admin(request)
    store = _get_auth_store(request)
    records = store.get_policy_audit_records(user_id)
    return [
        PolicyAuditRecordResponse(
            audit_id=r.audit_id,
            actor_id=r.actor_id,
            target_user_id=r.target_user_id,
            action=r.action,
            snapshot_before=r.snapshot_before,
            snapshot_after=r.snapshot_after,
            changed_at=r.changed_at.isoformat(),
            changed_fields=r.changed_fields(),
        )
        for r in records
    ]


def _ent_to_snapshot(ent: Optional[Entitlement]) -> dict:
    if ent is None:
        return {}
    return {
        "license_status": ent.license_status.value,
        "expires_at": ent.expires_at.isoformat() if ent.expires_at else None,
        "trading_enabled": ent.trading_enabled,
        "allowed_features": ent.allowed_features,
        "visible_panels": ent.visible_panels,
        "visible_rules": ent.visible_rules,
        "editable_rules": ent.editable_rules,
        "blocked_reason_messages": ent.blocked_reason_messages,
    }


def _ent_to_response(ent: Entitlement) -> EntitlementResponse:
    return EntitlementResponse(
        user_id=ent.user_id,
        license_status=ent.license_status.value,
        expires_at=ent.expires_at.isoformat() if ent.expires_at else None,
        trading_enabled=ent.trading_enabled,
        allowed_features=ent.allowed_features,
        visible_panels=ent.visible_panels,
        visible_rules=ent.visible_rules,
        editable_rules=ent.editable_rules,
        blocked_reason_messages=ent.blocked_reason_messages,
    )
