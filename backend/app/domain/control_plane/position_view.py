"""PositionView — read model for a single position in the control plane."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PositionView:
    position_id: str
    event_key: str
    side: str
    status: str  # "open" or "closed"

    # Price fields — trigger / fill / current are never collapsed
    trigger_price: float
    entry_fill_price: float
    current_price: float
    exit_fill_price: float  # 0.0 when position is still open

    # Move values — three distinct moments
    trigger_move_value: float
    fill_move_value: float
    current_move_value: float

    # PnL
    realized_pnl: float
    unrealized_pnl: float

    # Metadata
    entry_reason: str
    exit_reason: str  # empty string when open
    opened_at: str
    closed_at: Optional[str]  # None when open
