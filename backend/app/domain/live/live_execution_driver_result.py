"""Live execution driver result — v1.0.4.

Produced by LiveExecutionDriver.run().

driver_stage: string value of LiveExecutionStage from the orchestration layer.

submit_result:         outcome_status string from adapter submit response.
update_result:         update_type string from last fill stream poll.
reconciliation_result: reconciliation_status string from order event reconciler.
accounting_result:     dict carrying fill summary (filled_size, fill_price, pnl fields).

Fail-closed rules:
  - completed=True only on full fill or cancellation acknowledged by orchestrator.
  - terminal_failure=True on submit reject / auth error / unknown update.
  - retryable=True on transient errors (timeout / 429 / 5xx).
  - blocker_reasons populated when outbound guard or preflight blocks execution.
  - No fake success: completed=False and realized_pnl=0.0 until real fill confirmed.
"""
from dataclasses import dataclass, field


@dataclass
class LiveExecutionDriverResult:
    """Full result of one live execution driver cycle."""

    # Identity
    event_key: str
    order_id: str = ""
    client_order_id: str = ""

    # Sub-layer results (string representations)
    submit_result: str = ""
    update_result: str = ""
    reconciliation_result: str = ""
    accounting_result: dict = field(default_factory=dict)

    # Orchestration output
    driver_stage: str = ""
    completed: bool = False
    retryable: bool = False
    terminal_failure: bool = False
    blocker_reasons: list = field(default_factory=list)

    # Poll metadata
    poll_attempts: int = 0
    last_update_status: str = ""

    # Fill fields (populated only when fill received)
    last_fill_price: float = 0.0
    last_filled_size: float = 0.0

    # Accounting fields (populated from fill data)
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    current_balance: float = 0.0

    # Audit trail
    raw_driver_trace: list = field(default_factory=list)
