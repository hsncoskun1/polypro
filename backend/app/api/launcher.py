"""Launcher authority status endpoint — v1.1.0.

GET /api/v1/launcher/status
Returns whether the backend was started via the launcher (grant token present)
and whether launcher grant is required for operational access.

This endpoint is always open (no auth, no grant required) so the frontend
can check it before showing the user panel.
"""
from fastapi import APIRouter
from app.core.config import LAUNCHER_GRANT_TOKEN, REQUIRE_LAUNCHER_GRANT

router = APIRouter(prefix="/api/v1/launcher", tags=["launcher"])


@router.get("/status")
def launcher_status() -> dict:
    """Return launcher authority state.

    launched: True if LAUNCHER_GRANT_TOKEN env var is set and non-empty.
    grant_required: True if REQUIRE_LAUNCHER_GRANT is enabled.
    """
    return {
        "launched": bool(LAUNCHER_GRANT_TOKEN),
        "grant_required": REQUIRE_LAUNCHER_GRANT,
    }
