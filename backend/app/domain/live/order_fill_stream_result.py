"""Order fill stream result — v1.0.3.

Produced by PolymarketHttpClient.execute_get_fill_stream_update.

update_type values:
  "full_fill"    — filled_size > 0 and remaining_size == 0
  "partial_fill" — filled_size > 0 and remaining_size > 0
  "no_update"    — order active but no fill yet (LIVE / MATCHED / DELAYED)
  "cancelled"    — order CANCELLED at exchange
  "rejected"     — order UNMATCHED (rejected/unmatched at exchange)
  "unknown"      — unrecognized status (fail-closed classification)

source values:
  "poll" — result obtained via HTTP polling (GET /order/{id})
  ""     — source unknown (error path)

Fail-closed rules:
  - Malformed / missing status → terminal_failure=True
  - Auth error → terminal_failure=True
  - Timeout / 429 / 5xx → retryable=True
  - Unknown HTTP → terminal_failure=True
  - stream_connected=True only when a successful HTTP 200 was received
"""
from dataclasses import dataclass, field


@dataclass
class OrderFillStreamResult:
    """Result of an order fill stream update fetch."""

    # Identity
    order_id: str = ""
    client_order_id: str = ""

    # Update classification
    update_type: str = ""       # full_fill / partial_fill / no_update / cancelled / rejected / unknown
    order_status: str = ""      # raw status string from exchange (LIVE, MATCHED, CANCELLED, ...)

    # Fill fields (populated only when filled_size > 0)
    filled_size: float = 0.0
    remaining_size: float = 0.0
    fill_price: float = 0.0

    # Metadata
    updated_at: str = ""        # Unix timestamp string at time of fetch
    source: str = ""            # "poll" or ""
    stream_connected: bool = False

    # Error / retry state
    retryable: bool = False
    terminal_failure: bool = False
    reject_reason: str = ""

    # Raw and normalized payloads
    raw_update_payload: dict = field(default_factory=dict)
    normalized_update_result: str = ""
