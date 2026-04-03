"""Control plane API schema — v0.8.8."""
from typing import List, Optional
from pydantic import BaseModel


class PositionViewSchema(BaseModel):
    position_id: str
    event_key: str
    side: str
    status: str

    trigger_price: float
    entry_fill_price: float
    current_price: float
    exit_fill_price: float

    trigger_move_value: float
    fill_move_value: float
    current_move_value: float

    realized_pnl: float
    unrealized_pnl: float

    entry_reason: str
    exit_reason: str
    opened_at: str
    closed_at: Optional[str]


class ControlPlaneResponse(BaseModel):
    # Positions
    open_positions: List[PositionViewSchema]
    closed_positions: List[PositionViewSchema]

    # Session PnL
    session_realized_pnl: float
    session_unrealized_pnl: float
    session_total_pnl: float

    # Balance
    total_balance: float
    available_balance: float
    current_balance: float
    session_start_balance: float

    # Claim
    claim_status: str
    claim_available: bool
    claimed_amount: float
    settlement_completed_at: Optional[str]

    # Gate state
    release_ready: bool
    live_applied_testing_ready: bool
    live_mode_ui_blocked: bool
    blocked_reason_messages: List[str]
