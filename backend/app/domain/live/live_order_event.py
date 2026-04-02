"""Live order event record model — v0.7.6."""
from dataclasses import dataclass
from app.domain.live.live_order_event_type import LiveOrderEventType


@dataclass
class LiveOrderEvent:
    order_id: str
    event_type: LiveOrderEventType
    client_order_id: str = ""
    event_timestamp: str = ""
    side: str = ""
    requested_size: float = 0.0
    filled_size: float = 0.0
    remaining_size: float = 0.0
    limit_price: float = 0.0
    reject_reason: str = ""
    is_terminal: bool = False
