"""External replace request payload — v0.8.0.

Models the payload that would be sent to the production exchange for order replacement.
No network calls here — seam for future HTTP/WS client.
"""
from dataclasses import dataclass


@dataclass
class ExternalReplacePayload:
    order_id: str
    new_limit_price: float
    new_size: float
    client_order_id: str = ""
    raw_payload: str = ""
