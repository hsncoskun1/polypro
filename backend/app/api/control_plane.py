"""Control plane API endpoint — v0.8.8.

Returns the current user control plane state for the frontend.
No live trading data is connected in this version — returns empty/default state.
live_applied_testing_ready is never auto-enabled.
Secrets are never included in this response.
"""
from fastapi import APIRouter
from app.api.schemas.control_plane import ControlPlaneResponse, PositionViewSchema
from app.domain.claim.claim_status import ClaimStatus

router = APIRouter()

_BLOCKED_MESSAGE_TR = "Canlı uygulamalı test henüz yetkilendirilmedi."


def _build_control_plane_response() -> ControlPlaneResponse:
    """
    Build the current control plane state.

    Design:
    - open_positions / closed_positions: empty — no live data source connected yet
    - all PnL and balance fields: 0.0 default — no live accounting wired yet
    - claim_status: not_claimable_outcome_unknown — no settlement state
    - release_ready: True — release gate cleared
    - live_applied_testing_ready: False — NEVER auto-enabled
    - live_mode_ui_blocked: True — user cannot reach live trading until gate authorized
    """
    live_applied_testing_ready = False  # never auto-enabled
    release_ready = True
    live_mode_ui_blocked = not live_applied_testing_ready

    blocked_messages = []
    if live_mode_ui_blocked:
        blocked_messages.append(_BLOCKED_MESSAGE_TR)

    return ControlPlaneResponse(
        open_positions=[],
        closed_positions=[],
        session_realized_pnl=0.0,
        session_unrealized_pnl=0.0,
        session_total_pnl=0.0,
        total_balance=0.0,
        available_balance=0.0,
        current_balance=0.0,
        session_start_balance=0.0,
        claim_status=ClaimStatus.NOT_CLAIMABLE_OUTCOME_UNKNOWN.value,
        claim_available=False,
        claimed_amount=0.0,
        settlement_completed_at=None,
        release_ready=release_ready,
        live_applied_testing_ready=live_applied_testing_ready,
        live_mode_ui_blocked=live_mode_ui_blocked,
        blocked_reason_messages=blocked_messages,
    )


@router.get("/control-plane", response_model=ControlPlaneResponse)
def get_control_plane() -> ControlPlaneResponse:
    """Return current user control plane state. No secrets included."""
    return _build_control_plane_response()
