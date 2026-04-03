"""Order fill stream request payload — v1.0.3."""
from dataclasses import dataclass


@dataclass
class OrderFillStreamPayload:
    """Request descriptor for an order fill stream fetch.

    Carries the order_id to look up and optional client_order_id for
    correlation with internal event records.
    """
    order_id: str = ""
    client_order_id: str = ""
