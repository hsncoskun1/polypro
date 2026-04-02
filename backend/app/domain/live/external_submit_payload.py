"""External submit request payload — v0.8.0.

Models the payload that would be sent to the production exchange for order submission.
No network calls here — seam for future HTTP/WS client.
"""
from dataclasses import dataclass


@dataclass
class ExternalSubmitPayload:
    order_id: str
    market_id: str
    side: str
    size: float
    limit_price: float
    client_order_id: str = ""
    raw_payload: str = ""
