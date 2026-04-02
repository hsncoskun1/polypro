"""Force sell evaluator — produces force sell decisions from position context.

Design decisions:
- Entry/fill-based adverse move, NOT PTB-based. This is a binding project decision.
- Adverse move is side-aware:
    YES/UP: adverse_move = entry_fill_price - current_price
    NO/DOWN: adverse_move = current_price - entry_fill_price
- Three independent conditions: time, pnl-loss, entry/fill adverse delta.
- Combinator (any/all) applies only when 2+ conditions are enabled.
- Reason code is specific when exactly 1 condition is enabled.
- Reason code is combined when 2+ conditions are enabled and the combinator fires.
- Never returns None. All paths return a fully populated ForceSellDecision.
- Force sell lives in exit policy evaluator layer — separate from execution.
- Correct flow: open_position → exit_policy_evaluator → exit_decision → execution_exit
- Persistence: NOT in scope (v0.5.3).
- PnL accounting: NOT in scope.
"""
from app.domain.force_sell.force_sell_context import ForceSellContext
from app.domain.force_sell.force_sell_decision import ForceSellDecision


def _time_triggered(ctx: ForceSellContext) -> bool:
    return ctx.force_sell_time_enabled and ctx.time_remaining <= ctx.force_sell_time_seconds


def _pnl_loss_triggered(ctx: ForceSellContext) -> bool:
    return ctx.force_sell_pnl_loss_enabled and ctx.current_pnl < 0


def _entry_delta_triggered(ctx: ForceSellContext) -> bool:
    if not ctx.force_sell_entry_delta_enabled:
        return False
    if ctx.side in ("YES", "UP"):
        adverse_move = ctx.entry_fill_price - ctx.current_price
    else:  # "NO" / "DOWN"
        adverse_move = ctx.current_price - ctx.entry_fill_price
    return adverse_move >= ctx.force_sell_entry_delta_threshold


def evaluate_force_sell(ctx: ForceSellContext) -> ForceSellDecision:
    """Evaluate whether a position should be force-sold.

    Checks each enabled condition and applies the combinator logic.
    For a single enabled condition: returns a specific reason code.
    For multiple enabled conditions: applies any/all combinator and
    returns a combined reason code.

    Args:
        ctx: The force sell context with position data and rule config.

    Returns:
        ForceSellDecision with should_force_sell=True and a reason,
        or should_force_sell=False with empty reason.
    """
    enabled_conditions = [
        ("force_sell_time", _time_triggered(ctx)),
        ("force_sell_pnl_loss", _pnl_loss_triggered(ctx)),
        ("force_sell_entry_delta", _entry_delta_triggered(ctx)),
    ]

    # Filter to only enabled (configured) conditions
    enabled = [
        (name, fired)
        for name, fired in [
            ("force_sell_time",
             ctx.force_sell_time_enabled),
            ("force_sell_pnl_loss",
             ctx.force_sell_pnl_loss_enabled),
            ("force_sell_entry_delta",
             ctx.force_sell_entry_delta_enabled),
        ]
        if fired
    ]
    enabled_count = len(enabled)

    if enabled_count == 0:
        return ForceSellDecision(should_force_sell=False, reason="")

    # Evaluate which of the enabled conditions have triggered
    triggered_names = [
        name for name, _ in enabled
        if _condition_fired(name, ctx)
    ]
    triggered_count = len(triggered_names)

    if triggered_count == 0:
        return ForceSellDecision(should_force_sell=False, reason="")

    # Single enabled condition
    if enabled_count == 1:
        return ForceSellDecision(
            should_force_sell=True,
            reason=triggered_names[0],
        )

    # Multiple enabled conditions — apply combinator
    if ctx.force_sell_logic == "any":
        return ForceSellDecision(
            should_force_sell=True,
            reason="force_sell_combined_any",
        )
    else:  # "all"
        if triggered_count == enabled_count:
            return ForceSellDecision(
                should_force_sell=True,
                reason="force_sell_combined_all",
            )
        return ForceSellDecision(should_force_sell=False, reason="")


def _condition_fired(name: str, ctx: ForceSellContext) -> bool:
    """Dispatch condition check by name."""
    if name == "force_sell_time":
        return _time_triggered(ctx)
    if name == "force_sell_pnl_loss":
        return _pnl_loss_triggered(ctx)
    if name == "force_sell_entry_delta":
        return _entry_delta_triggered(ctx)
    return False
