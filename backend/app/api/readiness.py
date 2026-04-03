"""Readiness API endpoint — v0.8.7.

Returns the current launcher/readiness state for the frontend.
launcher_blocked=True by default — live applied testing is never auto-enabled.
Secrets are never included in this response.
"""
import os
from fastapi import APIRouter
from app.api.schemas.readiness import ReadinessResponse

router = APIRouter()

_FRONTEND_PORT = int(os.environ.get("FRONTEND_PORT", "5173"))
_BACKEND_PORT = int(os.environ.get("APP_PORT", "8000"))
_POLL_INTERVAL_MS = int(os.environ.get("READINESS_POLL_INTERVAL_MS", "5000"))

# Turkish blocked reason messages aligned with surface_label_mapper
_BLOCKED_MESSAGES_TR = {
    "live_applied_testing_not_authorized": (
        "Canlı uygulamalı test henüz yetkilendirilmedi."
    ),
    "backend_not_ready": "Backend hazır değil.",
    "release_not_ready": "Yayın hazırlığı tamamlanmadı.",
}


def _build_readiness_response() -> ReadinessResponse:
    """
    Build the current readiness state.

    Design:
    - backend_ready=True: the backend is reachable (this endpoint responds)
    - setup_completed=True: backend started without error
    - update_required=False: no forced update in this version
    - preflight_passed=False: live mode not requested (simulation default)
    - final_backend_ready=True: all non-live backend links complete (v0.8.3)
    - release_ready=True: all release readiness links complete (v0.8.4)
    - live_applied_testing_ready=False: NEVER auto-enabled (always explicit gate)
    - launcher_blocked=True: user needs live gate authorization to proceed
    - continue_destination=None: blocked, no destination
    """
    live_applied_testing_ready = False  # never auto-enabled
    release_ready = True
    final_backend_ready = True
    backend_ready = True
    setup_completed = True
    preflight_passed = False  # simulation default — live not requested

    launcher_blocked = not live_applied_testing_ready

    blocked_messages = []
    if not live_applied_testing_ready:
        blocked_messages.append(
            _BLOCKED_MESSAGES_TR["live_applied_testing_not_authorized"]
        )

    continue_destination = None if launcher_blocked else "/user"

    return ReadinessResponse(
        launcher_blocked=launcher_blocked,
        setup_completed=setup_completed,
        update_required=False,
        preflight_passed=preflight_passed,
        backend_ready=backend_ready,
        final_backend_ready=final_backend_ready,
        release_ready=release_ready,
        live_applied_testing_ready=live_applied_testing_ready,
        blocked_reason_messages=blocked_messages,
        continue_destination=continue_destination,
        frontend_port=_FRONTEND_PORT,
        backend_port=_BACKEND_PORT,
        readiness_poll_interval_ms=_POLL_INTERVAL_MS,
    )


@router.get("/readiness", response_model=ReadinessResponse)
def get_readiness() -> ReadinessResponse:
    """Return current launcher/readiness state. No secrets included."""
    return _build_readiness_response()
