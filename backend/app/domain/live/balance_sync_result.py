"""Balance sync result — v1.0.2.

Produced by PolymarketHttpClient.execute_get_balance.

Fields:
  total_balance           — total account balance from exchange
  available_balance       — balance available to place new orders
  current_balance         — current balance (available minus reserved)
  currency                — collateral currency (USDC for Polymarket)
  synced_at               — Unix timestamp string at time of fetch
  sync_success            — True only if balance was successfully read
  retryable               — True if a transient error occurred (timeout / 5xx / 429)
  terminal_failure        — True if no retry will help (auth error / malformed)
  reject_reason           — short string reason when sync_success=False
  raw_balance_payload     — raw dict from exchange response
  normalized_balance_result — human-readable one-line summary for reporting

Fail-closed rules:
  - Missing or malformed balance field → sync_success=False, terminal_failure=True
  - Auth error → sync_success=False, terminal_failure=True
  - Timeout / 429 / 5xx → sync_success=False, retryable=True
  - Unknown HTTP error → sync_success=False, terminal_failure=True
  - balance=0.0 is ONLY set on a real zero balance, never as a fake default
"""
from dataclasses import dataclass, field


@dataclass
class BalanceSyncResult:
    """Result of a balance fetch + sync operation against the exchange."""

    # Balance fields (only populated on sync_success=True)
    total_balance: float = 0.0
    available_balance: float = 0.0
    current_balance: float = 0.0
    currency: str = ""

    # Sync metadata
    synced_at: str = ""
    sync_success: bool = False

    # Error / retry state
    retryable: bool = False
    terminal_failure: bool = False
    reject_reason: str = ""

    # Raw and normalized payloads
    raw_balance_payload: dict = field(default_factory=dict)
    normalized_balance_result: str = ""
