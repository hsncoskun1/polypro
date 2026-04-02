"""Accounting snapshot — full output record of execution fill + PnL accounting.

Design decisions:
- Contains all minimum required fields per the v0.5.4 specification.
- Produced by entry_fill_accounting or exit_fill_accounting helpers.
- Combines: trigger/submitted/fill/current price separation, move values,
  PnL fields, session fields, and balance fields.
- PnL is always fill-price based — order_submitted_price is carried for
  reporting only and must never be used as PnL basis.
- unrealized_pnl is 0.0 after position is closed.
- realized_pnl is 0.0 before position is closed.
- current_balance = session_start_balance + session_realized_pnl.
  Unrealized PnL is not added to balance until realized.
- claim_adjusted_balance_effect is a seam field; not applied to balance here.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AccountingSnapshot:
    """Full accounting snapshot produced after entry or exit fill.

    Fields:
        side: Trade direction — "YES" or "NO".
        entry_trigger_price: Price at rule trigger.
        entry_order_submitted_price: Price at order submission (report only).
        entry_fill_price: Actual fill price. Authoritative PnL basis.
        entry_trigger_move_value: Price move from trigger to fill.
        entry_fill_move_value: Price move from entry fill to current/exit.
        current_price: Current market price.
        current_move_value: Move from entry fill to current (side-aware).
        exit_trigger_price: Exit trigger price. 0.0 if position open.
        exit_order_submitted_price: Exit order submitted price (report only).
        exit_fill_price: Actual exit fill price. 0.0 if position open.
        requested_size: Size requested at entry.
        filled_size: Actual filled size.
        unrealized_pnl: Unrealized PnL for open position. 0.0 if closed.
        realized_pnl: Realized PnL from this position's exit. 0.0 if open.
        session_realized_pnl: Total realized PnL this session (including prior).
        session_unrealized_pnl: Unrealized PnL across all open positions this session.
        session_total_pnl: session_realized_pnl + session_unrealized_pnl.
        total_balance: Carried total balance (not authoritative this turn).
        available_balance: Carried available balance.
        session_start_balance: Balance at session start.
        current_balance: session_start_balance + session_realized_pnl.
        claim_adjusted_balance_effect: Seam for future claim integration.
    """

    side: str
    entry_trigger_price: float
    entry_order_submitted_price: float
    entry_fill_price: float
    entry_trigger_move_value: float
    entry_fill_move_value: float
    current_price: float
    current_move_value: float
    exit_trigger_price: float
    exit_order_submitted_price: float
    exit_fill_price: float
    requested_size: float
    filled_size: float
    unrealized_pnl: float
    realized_pnl: float
    session_realized_pnl: float
    session_unrealized_pnl: float
    session_total_pnl: float
    total_balance: float
    available_balance: float
    session_start_balance: float
    current_balance: float
    claim_adjusted_balance_effect: float
