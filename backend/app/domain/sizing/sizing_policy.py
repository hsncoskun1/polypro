"""SizingPolicy — admin-controlled order sizing constraints."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class SizingPolicy:
    min_order_size: float
    max_order_size: float
    min_available_balance_to_trade: float
    allowed_sizing_modes: List[str] = field(default_factory=list)
