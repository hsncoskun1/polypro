"""GET /admin/control-plane — admin operational control and reporting endpoint.

Returns full AdminControlPlaneResponse:
- Operational control state (safe stop, scheduler, global disable, config)
- Financial summary (balance/PnL)
- Blocked/fill/claim/alert event lists
- Release gate fields

All values are default/empty in current state — no live sources yet.
live_applied_testing_ready is always False and never auto-enabled.
Secrets are never in the response.
"""
from fastapi import APIRouter
from app.api.schemas.admin_control_plane import AdminControlPlaneResponse

router = APIRouter()


def _build_admin_control_plane_response() -> AdminControlPlaneResponse:
    return AdminControlPlaneResponse(
        # Operational control — default safe state
        safe_stop_active=False,
        safe_stop_reason="",
        scheduler_enabled=True,
        global_disable_active=False,
        config_reload_available=True,
        config_reset_available=True,
        # Financial — no live accounting yet
        total_balance=0.0,
        available_balance=0.0,
        current_balance=0.0,
        session_start_balance=0.0,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        session_total_pnl=0.0,
        claim_adjusted_balance_effect=0.0,
        # Event lists — empty until live sources wired
        blocked_trades=[],
        blocked_rules=[],
        blocked_risk_events=[],
        execution_fill_events=[],
        claim_events=[],
        operational_alerts=[],
        # Release gate
        release_ready=True,
        live_applied_testing_ready=False,  # never auto-enabled
    )


@router.get("/admin/control-plane", response_model=AdminControlPlaneResponse)
def get_admin_control_plane() -> AdminControlPlaneResponse:
    """Admin operational control and reporting surface.

    Broader than the user-facing /control-plane.
    Secrets are never included.
    live_applied_testing_ready is always False.
    """
    return _build_admin_control_plane_response()
