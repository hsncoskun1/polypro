import os

from fastapi import Header, HTTPException, Request


def verify_trigger_auth(authorization: str | None = Header(default=None)) -> None:
    """Verify Bearer token for the discovery trigger endpoint.

    Reads expected token from TRIGGER_AUTH_TOKEN env var at request time.
    If the env var is not set or empty, auth is not enforced (shell mode).
    If set, requires 'Authorization: Bearer <token>' with a matching value.
    Missing or wrong token raises HTTP 401. No silent fallback.
    """
    expected = os.getenv("TRIGGER_AUTH_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=500,
            detail="Auth not configured: TRIGGER_AUTH_TOKEN is not set",
        )

    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value:
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    if value != expected:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- v1.0.5 Session auth dependencies ---

from app.domain.auth.user import User


def get_current_user(request: Request) -> User:
    """Resolve user from X-Session-Token header. Raises 401 if invalid or expired."""
    token = request.headers.get("X-Session-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Session token required")
    auth_store = getattr(request.app.state, "auth_store", None)
    if auth_store is None:
        raise HTTPException(status_code=500, detail="Auth store not initialized")
    user = auth_store.get_user_by_session_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    from app.domain.auth.auth_service import is_session_valid
    if not is_session_valid(user):
        raise HTTPException(status_code=401, detail="Session expired")
    return user


def require_trading_enabled(request: Request) -> None:
    """Block trading actions if user license is not active. Raises 403 if trading disabled."""
    token = request.headers.get("X-Session-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Session token required")
    auth_store = getattr(request.app.state, "auth_store", None)
    if auth_store is None:
        raise HTTPException(status_code=500, detail="Auth store not initialized")
    user = auth_store.get_user_by_session_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    ent = auth_store.get_entitlement(user.user_id)
    from app.domain.entitlement.entitlement_service import is_trading_enabled
    if not is_trading_enabled(ent):
        raise HTTPException(status_code=403, detail="Trading disabled: license not active or expired")
