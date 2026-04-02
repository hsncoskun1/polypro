"""Adapter replace request contract — v0.7.8."""
from dataclasses import dataclass


@dataclass
class AdapterReplaceRequest:
    order_id: str
    event_key: str
    new_limit_price: float
    new_size: float
