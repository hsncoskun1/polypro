"""RiskContext — input contract for risk engine evaluation."""
from dataclasses import dataclass


@dataclass
class RiskContext:
    # Daily loss cap — positive value represents max allowable loss
    daily_loss_limit: float
    current_daily_loss: float  # cumulative loss today (positive = loss incurred)

    # Daily trade cap
    daily_trade_cap: int
    current_daily_trade_count: int

    # Per-event open position limit
    event_limit: int
    current_event_open_positions: int

    # Total concurrent open position limit
    max_concurrent_positions: int
    current_open_positions: int

    # Position size constraints
    min_position_size: float
    max_position_size: float
    requested_position_size: float
