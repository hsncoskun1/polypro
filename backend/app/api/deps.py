import os

from fastapi import Header, HTTPException


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
