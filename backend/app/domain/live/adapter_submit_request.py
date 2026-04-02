"""Adapter submit request contract — v0.7.8."""
from dataclasses import dataclass


@dataclass
class AdapterSubmitRequest:
    order_id: str
    event_key: str
    market_id: str
    side: str
    size: float
    limit_price: float
