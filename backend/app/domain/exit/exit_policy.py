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
- Force sell: NOT in scope (v0.5.2+).
- Persistence: NOT in scope (v0.5.2+).
- Runtime state is not mutated here — evaluator is a pure function.
"""
from app.domain.exit.exit_context import ExitContext
from app.domain.exit.exit_decision import ExitDecision


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
