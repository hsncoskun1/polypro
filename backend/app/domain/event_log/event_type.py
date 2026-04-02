"""Event type enumeration — lifecycle events in the trading position flow.

Design decisions:
- Two-phase model for both entry and exit: order_submitted → filled.
  These moments must not be collapsed.
- claim_available and claim_completed are seam events — they will be
  populated when claim/settlement is implemented (future scope).
- balance_updated is a seam event for future external balance integration.
- All event types are string-valued for easy serialization.
"""
from enum import Enum


class EventType(str, Enum):
    """Lifecycle event types for the trading position flow.

    Entry flow:    decision_passed → entry_order_submitted → entry_filled → position_opened
    Exit flow:     exit_triggered → exit_order_submitted → exit_filled → position_closed
    Post-close:    claim_available (seam) → claim_completed (seam) → balance_updated (seam)
    """

    DECISION_PASSED = "decision_passed"
    ENTRY_ORDER_SUBMITTED = "entry_order_submitted"
    ENTRY_FILLED = "entry_filled"
    POSITION_OPENED = "position_opened"
    EXIT_TRIGGERED = "exit_triggered"
    EXIT_ORDER_SUBMITTED = "exit_order_submitted"
    EXIT_FILLED = "exit_filled"
    POSITION_CLOSED = "position_closed"
    CLAIM_AVAILABLE = "claim_available"
    CLAIM_COMPLETED = "claim_completed"
    BALANCE_UPDATED = "balance_updated"
