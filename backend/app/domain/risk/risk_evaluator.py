"""risk_evaluator — hard risk block evaluation.

All checks run — multiple blockers are collected and returned together.
risk_allowed is True only when blocker_reasons is empty.
"""
from app.domain.risk.risk_context import RiskContext
from app.domain.risk.risk_result import RiskResult


def evaluate_risk(ctx: RiskContext) -> RiskResult:
    """Evaluate all hard risk constraints against current session state.

    All six checks run regardless of earlier results.
    All active blockers are collected and returned in blocker_reasons.
    risk_allowed = True only when no blockers are found.
    """
    blockers = []

    # 1. Daily loss limit
    if ctx.current_daily_loss >= ctx.daily_loss_limit:
        blockers.append("daily_loss_limit_exceeded")

    # 2. Daily trade cap
    if ctx.current_daily_trade_count >= ctx.daily_trade_cap:
        blockers.append("daily_trade_cap_exceeded")

    # 3. Per-event open position limit
    if ctx.current_event_open_positions >= ctx.event_limit:
        blockers.append("event_limit_exceeded")

    # 4. Total concurrent open positions
    if ctx.current_open_positions >= ctx.max_concurrent_positions:
        blockers.append("max_concurrent_positions_exceeded")

    # 5. Requested position size below minimum
    if ctx.requested_position_size < ctx.min_position_size:
        blockers.append("below_min_position_size")

    # 6. Requested position size above maximum
    if ctx.requested_position_size > ctx.max_position_size:
        blockers.append("above_max_position_size")

    return RiskResult(
        risk_allowed=len(blockers) == 0,
        blocker_reasons=blockers,
    )
