"""Live order replace request contract — v0.7.5."""
from dataclasses import dataclass


@dataclass
class LiveReplaceRequest:
    order_id: str
    new_limit_price: float
    new_size: float
    outbound_allowed: bool
    preflight_passed: bool
