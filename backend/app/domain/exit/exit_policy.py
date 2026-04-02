"""Exit policy evaluator — produces exit decisions from position context.

Design decisions:
- Evaluation order: stop_loss → take_profit → timeout → no_exit.
  Stop loss takes priority as capital preservation is the primary concern.
- Direction-aware: profit and loss moves are computed relative to side.
  YES: profit when price rises, loss when price falls.
  NO: profit when price falls, loss when price rises.
- Execution is separate from decision: this evaluator produces an ExitDecision;
  the caller applies it via simulate_exit() in the execution layer.
- Never returns None. All paths return a fully populated ExitDecision.
- Force sell (v0.5.2): integrated via evaluate_exit_policy_with_force_sell().
  Force sell is evaluated first; if triggered, it takes priority over all other
  conditions. evaluate_exit_policy() is unchanged.
- Persistence: NOT in scope (v0.5.3+).
- Runtime state is not mutated here — evaluator is a pure function.
"""
from app.domain.exit.exit_context import ExitContext
from app.domain.exit.exit_decision import ExitDecision
from app.domain.force_sell.force_sell_context import ForceSellContext
from app.domain.force_sell.force_sell_evaluator import evaluate_force_sell


def evaluate_exit_policy(ctx: ExitContext) -> ExitDecision:
    """Evaluate whether a position should be exited.

    Checks stop loss, take profit, and timeout conditions in priority order.
    Returns the first triggered condition. Returns no-exit decision if none apply.

    Args:
        ctx: The exit context with position data and thresholds.

    Returns:
        ExitDecision with should_exit=True and a reason, or should_exit=False.
    """
    if ctx.side == "YES":
        profit_move = ctx.current_price - ctx.entry_price
        loss_move = ctx.entry_price - ctx.current_price
    else:  # "NO"
        profit_move = ctx.entry_price - ctx.current_price
        loss_move = ctx.current_price - ctx.entry_price

    if loss_move >= ctx.stop_loss_threshold:
        return ExitDecision(should_exit=True, exit_reason="stop_loss")

    if profit_move >= ctx.take_profit_threshold:
        return ExitDecision(should_exit=True, exit_reason="take_profit")

    if ctx.time_remaining <= 0:
        return ExitDecision(should_exit=True, exit_reason="timeout")

    return ExitDecision(should_exit=False, exit_reason="")


def evaluate_exit_policy_with_force_sell(
    exit_ctx: ExitContext,
    force_sell_ctx: ForceSellContext,
) -> ExitDecision:
    """Evaluate exit policy with force sell integration.

    Force sell is evaluated first. If it triggers, its reason is returned as
    the exit reason and normal exit policy conditions are not checked.
    If force sell does not trigger, delegates to evaluate_exit_policy().

    Args:
        exit_ctx: The exit context with position data and thresholds.
        force_sell_ctx: The force sell context with condition config.

    Returns:
        ExitDecision — force sell reason if triggered, otherwise normal exit decision.
    """
    force_sell_decision = evaluate_force_sell(force_sell_ctx)
    if force_sell_decision.should_force_sell:
        return ExitDecision(
            should_exit=True,
            exit_reason=force_sell_decision.reason,
        )
    return evaluate_exit_policy(exit_ctx)
