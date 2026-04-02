"""External cancel request payload — v0.8.0.

Models the payload that would be sent to the production exchange for order cancellation.
No network calls here — seam for future HTTP/WS client.
"""
from dataclasses import dataclass


@dataclass
class ExternalCancelPayload:
    order_id: str
    client_order_id: str = ""
    raw_payload: str = ""
