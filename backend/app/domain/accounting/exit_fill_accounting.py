"""Exit fill accounting — produces accounting snapshot after exit fill.

Design decisions:
- Called after exit fill is confirmed. Position is now CLOSED.
- realized_pnl = compute_realized_pnl(entry_fill, exit_fill). Fill-price based.
  Order submitted price is never used as PnL basis.
- unrealized_pnl is 0.0 after exit (position closed).
- session_unrealized_pnl is 0.0 for this position (it is now realized).
- current_balance = session_start_balance + session_realized_pnl.
- entry_fill_move_value = move from entry_fill to exit_fill (realized direction).
- current_price at exit = exit_fill_price.
- Exit price fields are populated from ctx.exit_* fields.
"""
from app.domain.accounting.accounting_context import AccountingContext
from app.domain.accounting.accounting_snapshot import AccountingSnapshot
from app.domain.accounting.pnl_evaluator import (
    compute_realized_pnl,
    compute_move_value,
)


def compute_exit_fill_accounting(ctx: AccountingContext) -> AccountingSnapshot:
    """Produce an accounting snapshot immediately after exit fill.

    Realized PnL is computed from entry fill vs exit fill price.
    Unrealized PnL is 0.0 — position is closed.

    Args:
        ctx: Accounting context with both entry and exit prices, sizes, and balance.
             exit_fill_price must be set (non-zero).

    Returns:
        AccountingSnapshot with all fields populated for a closed position.
    """
    realized_pnl = compute_realized_pnl(
        entry_fill_price=ctx.entry_fill_price,
        exit_fill_price=ctx.exit_fill_price,
        filled_size=ctx.filled_size,
        side=ctx.side,
    )
    unrealized_pnl = 0.0  # position closed

    session_realized_pnl = ctx.prior_session_realized_pnl + realized_pnl
    session_unrealized_pnl = 0.0  # this position is now closed
    session_total_pnl = session_realized_pnl + session_unrealized_pnl
    current_balance = ctx.session_start_balance + session_realized_pnl

    # Move from trigger to fill (slippage at entry)
    entry_trigger_move_value = compute_move_value(
        entry_fill_price=ctx.entry_trigger_price,
        comparison_price=ctx.entry_fill_price,
        side=ctx.side,
    )
    # Move from entry fill to exit fill (the realized move)
    entry_fill_move_value = compute_move_value(
        entry_fill_price=ctx.entry_fill_price,
        comparison_price=ctx.exit_fill_price,
        side=ctx.side,
    )
    # At exit, current_price = exit_fill_price
    current_move_value = entry_fill_move_value

    return AccountingSnapshot(
        side=ctx.side,
        entry_trigger_price=ctx.entry_trigger_price,
        entry_order_submitted_price=ctx.entry_order_submitted_price,
        entry_fill_price=ctx.entry_fill_price,
        entry_trigger_move_value=entry_trigger_move_value,
        entry_fill_move_value=entry_fill_move_value,
        current_price=ctx.exit_fill_price,
        current_move_value=current_move_value,
        exit_trigger_price=ctx.exit_trigger_price,
        exit_order_submitted_price=ctx.exit_order_submitted_price,
        exit_fill_price=ctx.exit_fill_price,
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
