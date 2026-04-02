"""ControlPlaneSnapshot — full simulation control plane read model."""
from dataclasses import dataclass, field
from typing import List, Optional
from app.domain.control_plane.position_view import PositionView


@dataclass
class ControlPlaneSnapshot:
    # Position lists — open and closed are always separate
    open_positions: List[PositionView] = field(default_factory=list)
    closed_positions: List[PositionView] = field(default_factory=list)

    # Session PnL — three distinct fields, never collapsed
    session_realized_pnl: float = 0.0
    session_unrealized_pnl: float = 0.0
    session_total_pnl: float = 0.0

    # Balance fields
    total_balance: float = 0.0
    available_balance: float = 0.0
    current_balance: float = 0.0
    session_start_balance: float = 0.0

    # Claim / settlement visibility — separate section
    claim_status: str = ""
    claim_available: bool = False
    claimed_amount: float = 0.0
    settlement_completed_at: Optional[str] = None
