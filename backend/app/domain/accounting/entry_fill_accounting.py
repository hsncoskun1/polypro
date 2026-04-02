"""Entry fill accounting — produces accounting snapshot after entry fill.

Design decisions:
- Called after entry fill is confirmed. Position is now OPEN.
- realized_pnl is 0.0 at entry (position not yet closed).
- unrealized_pnl = compute_unrealized_pnl(entry_fill, current_price).
- entry_fill_move_value = move from entry_fill_price to current_price (side-aware).
- entry_trigger_move_value = move from entry_trigger_price to entry_fill_price.
  This captures slippage between rule trigger and actual fill.
- current_balance = session_start_balance + session_realized_pnl.
  Unrealized PnL does not contribute to current_balance.
- exit price fields are 0.0 at entry (position not exited yet).
- PnL is fill-price based. Order submitted price carried for reporting only.
"""
from app.domain.accounting.accounting_context import AccountingContext
from app.domain.accounting.accounting_snapshot import AccountingSnapshot
from app.domain.accounting.pnl_evaluator import (
    compute_unrealized_pnl,
    compute_move_value,
)


def compute_entry_fill_accounting(ctx: AccountingContext) -> AccountingSnapshot:
    """Produce an accounting snapshot immediately after entry fill.

    Unrealized PnL is computed from entry fill vs current price.
    Realized PnL is 0.0 — position is open.

    Args:
        ctx: Accounting context with entry prices, sizes, and balance info.

    Returns:
        AccountingSnapshot with all fields populated for an open position.
    """
    unrealized_pnl = compute_unrealized_pnl(
        entry_fill_price=ctx.entry_fill_price,
        current_price=ctx.current_price,
        filled_size=ctx.filled_size,
        side=ctx.side,
    )
    realized_pnl = 0.0

    session_realized_pnl = ctx.prior_session_realized_pnl + realized_pnl
    session_unrealized_pnl = unrealized_pnl
    session_total_pnl = session_realized_pnl + session_unrealized_pnl
    current_balance = ctx.session_start_balance + session_realized_pnl

    # Move from trigger moment to fill moment (slippage)
    entry_trigger_move_value = compute_move_value(
        entry_fill_price=ctx.entry_trigger_price,
        comparison_price=ctx.entry_fill_price,
        side=ctx.side,
    )
    # Move from fill moment to current (unrealized direction)
    entry_fill_move_value = compute_move_value(
        entry_fill_price=ctx.entry_fill_price,
        comparison_price=ctx.current_price,
        side=ctx.side,
    )
    current_move_value = entry_fill_move_value

    return AccountingSnapshot(
        side=ctx.side,
        entry_trigger_price=ctx.entry_trigger_price,
        entry_order_submitted_price=ctx.entry_order_submitted_price,
        entry_fill_price=ctx.entry_fill_price,
        entry_trigger_move_value=entry_trigger_move_value,
        entry_fill_move_value=entry_fill_move_value,
        current_price=ctx.current_price,
        current_move_value=current_move_value,
        exit_trigger_price=0.0,
        exit_order_submitted_price=0.0,
        exit_fill_price=0.0,
        requested_size=ctx.requested_size,
        filled_size=ctx.filled_size,
        unrealized_pnl=unrealized_pnl,
        realized_pnl=realized_pnl,
        session_realized_pnl=session_realized_pnl,
        session_unrealized_pnl=session_unrealized_pnl,
        session_total_pnl=session_total_pnl,
        total_balance=ctx.total_balance,
        available_balance=ctx.available_balance,
        session_start_balance=ctx.session_start_balance,
        current_balance=current_balance,
        claim_adjusted_balance_effect=ctx.claim_adjusted_balance_effect,
    )
