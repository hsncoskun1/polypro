"""Accounting context — input to execution fill + PnL accounting calculations.

Design decisions:
- A single context covers both entry and exit fill scenarios.
  Exit price fields default to 0.0 when computing entry fill accounting.
- PnL is computed from fill_price, NOT from order_submitted_price.
  This is a binding project decision.
- trigger / submitted / fill / current are kept as separate fields.
  These moments must never be collapsed.
- prior_session_realized_pnl accumulates realized PnL from prior closed
  positions in the same session, enabling session-level PnL tracking.
- claim_adjusted_balance_effect is a seam field only; no claim logic runs here.
- total_balance / available_balance are carried as accounting fields.
  Real external balance queries are out of scope.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AccountingContext:
    """Input contract for execution fill + PnL accounting evaluation.

    Fields:
        side: Trade direction — "YES" or "NO".
        entry_trigger_price: Price at which the entry rule was triggered.
        entry_order_submitted_price: Price at which the entry order was submitted.
        entry_fill_price: Actual entry fill price. Authoritative PnL basis.
        exit_trigger_price: Price at which exit was triggered. 0.0 if position open.
        exit_order_submitted_price: Price at which exit order was submitted.
        exit_fill_price: Actual exit fill price. 0.0 if position still open.
        current_price: Current market price (used for unrealized PnL when open).
        requested_size: Size requested at entry.
        filled_size: Actual filled size.
        total_balance: Total account balance (carried, not authoritative this turn).
        available_balance: Available balance (carried, not authoritative this turn).
        session_start_balance: Balance at the start of the trading session.
        prior_session_realized_pnl: Realized PnL from earlier closed positions
            in the same session. Used for session-level PnL accumulation.
        claim_adjusted_balance_effect: Seam field for future claim integration.
            Does not affect PnL calculation this turn.
    """

    side: str
    entry_trigger_price: float
    entry_order_submitted_price: float
    entry_fill_price: float
    current_price: float
    requested_size: float
    filled_size: float
    total_balance: float
    available_balance: float
    session_start_balance: float
    exit_trigger_price: float = field(default=0.0)
    exit_order_submitted_price: float = field(default=0.0)
    exit_fill_price: float = field(default=0.0)
    prior_session_realized_pnl: float = field(default=0.0)
    claim_adjusted_balance_effect: float = field(default=0.0)
