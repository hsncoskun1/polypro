"""SizingContext — input contract for order sizing evaluation."""
from dataclasses import dataclass
from app.domain.sizing.sizing_mode import SizingMode
from app.domain.sizing.sizing_policy import SizingPolicy


@dataclass
class SizingContext:
    sizing_mode: SizingMode
    available_balance: float
    total_balance: float
    policy: SizingPolicy
    fixed_amount: float = 0.0
    available_balance_percent: float = 0.0
