"""SizingResult — output of order sizing evaluation."""
from dataclasses import dataclass


@dataclass
class SizingResult:
    size_allowed: bool
    normalized_order_amount: float
    sizing_reason: str
