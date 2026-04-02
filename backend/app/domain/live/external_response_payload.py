"""External response payload — v0.8.0.

Models the raw response received from the production exchange.
Shared across submit/cancel/replace/update operations.
No network calls here — seam for future HTTP/WS client.
"""
from dataclasses import dataclass


@dataclass
class ExternalResponsePayload:
    mapped_order_id: str = ""
    mapped_client_order_id: str = ""
    mapped_status: str = ""
    mapped_reject_reason: str = ""
    retryable: bool = False
    terminal_failure: bool = False
    raw_payload: str = ""
    received_at: str = ""
    filled_size: float = 0.0
    remaining_size: float = 0.0
