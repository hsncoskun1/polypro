"""control_plane_assembler — assembles ControlPlaneSnapshot from domain data."""
from typing import List, Optional
from app.domain.control_plane.control_plane_snapshot import ControlPlaneSnapshot
from app.domain.control_plane.position_view import PositionView


def assemble_control_plane_snapshot(
    open_positions: List[PositionView],
    closed_positions: List[PositionView],
    session_realized_pnl: float,
    session_unrealized_pnl: float,
    session_total_pnl: float,
    total_balance: float,
    available_balance: float,
    current_balance: float,
    session_start_balance: float,
    claim_status: str,
    claim_available: bool,
    claimed_amount: float,
    settlement_completed_at: Optional[str],
) -> ControlPlaneSnapshot:
    """Assemble a ControlPlaneSnapshot from pre-built domain data.

    This function does not compute values — it assembles an already-computed
    read model. All PnL, balance, and claim values are passed in from
    upstream domain evaluators (accounting, claim, sizing, risk).
    """
    return ControlPlaneSnapshot(
        open_positions=list(open_positions),
        closed_positions=list(closed_positions),
        session_realized_pnl=session_realized_pnl,
        session_unrealized_pnl=session_unrealized_pnl,
        session_total_pnl=session_total_pnl,
        total_balance=total_balance,
        available_balance=available_balance,
        current_balance=current_balance,
        session_start_balance=session_start_balance,
        claim_status=claim_status,
        claim_available=claim_available,
        claimed_amount=claimed_amount,
        settlement_completed_at=settlement_completed_at,
    )
