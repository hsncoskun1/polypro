"""User-facing entitlement route — v1.0.5."""
from fastapi import APIRouter, HTTPException, Request

from app.api.schemas.auth import EntitlementResponse
from app.domain.entitlement.entitlement import Entitlement
from app.domain.entitlement.license_status import LicenseStatus

router = APIRouter(prefix="/api/v1/user", tags=["user"])


def _get_auth_store(request: Request):
    return request.app.state.auth_store


def _require_user(request: Request):
    """Resolve user from session token."""
    token = request.headers.get("X-Session-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Session token required")
    store = _get_auth_store(request)
    user = store.get_user_by_session_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return user


@router.get("/entitlement", response_model=EntitlementResponse)
def get_my_entitlement(request: Request):
    user = _require_user(request)
    store = _get_auth_store(request)
    ent = store.get_entitlement(user.user_id)
    if ent is None:
        # Return default locked entitlement
        ent = Entitlement(
            user_id=user.user_id,
            license_status=LicenseStatus.inactive,
            trading_enabled=False,
            blocked_reason_messages=["Trading disabled: license not active or expired."],
        )
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
