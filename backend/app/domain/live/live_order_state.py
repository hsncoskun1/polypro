"""Live order lifecycle state model — v0.7.6."""
from dataclasses import dataclass, field
from typing import Optional
from app.domain.live.live_order_event_type import LiveOrderEventType


@dataclass
class LiveOrderState:
    order_id: str
    client_order_id: str = ""
    side: str = ""
    requested_size: float = 0.0
    filled_size: float = 0.0
    remaining_size: float = 0.0
    limit_price: float = 0.0
    current_event_type: Optional[LiveOrderEventType] = None
    is_cancelled: bool = False
    is_filled: bool = False
    is_terminal: bool = False
    last_event_timestamp: str = ""
    event_count: int = 0
