"""Live order response contract — v0.7.4.

Carries the classified outcome of a live order submission.
Separate from submission seam (v0.7.3) — response is what came back from exchange.
"""
from dataclasses import dataclass, field
from app.domain.live.order_response_status import OrderResponseStatus


@dataclass
class LiveOrderResponse:
    order_id: str
    order_response_status: OrderResponseStatus

    # Size accounting
    requested_size: float
    accepted_size: float = 0.0
    filled_size: float = 0.0
    remaining_size: float = 0.0

    # Failure classification
    retryable: bool = False
    terminal_failure: bool = False
    reject_reason: str = ""

    # Audit timestamps
    response_received_at: str = ""
    fill_confirmed_at: str = ""
