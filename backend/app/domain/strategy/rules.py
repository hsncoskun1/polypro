"""Entry rule evaluators for the trading decision engine.

Each rule takes a RuleContext and returns a RuleResult.
Disabled rules return RuleState.DISABLED and are never counted as PASS.
locked_by_admin rules return RuleState.LOCKED_BY_ADMIN (reserved for v0.4.1 admin policy).
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.strategy.rule_result import RuleResult
from app.domain.strategy.rule_state import RuleState


@dataclass
class RuleContext:
    """All data a rule may need to evaluate an entry decision."""
    current_price: float
    ptb: float                      # price-to-beat (entry reference price)
    spread: float
    current_time: datetime
    trading_start: datetime         # daily window start (UTC)
    trading_end: datetime           # daily window end (UTC)
    move_threshold: float           # abs(current_price - ptb) must be >= this
    price_min: float
    price_max: float
    spread_max: float
    daily_event_count: int
    event_limit: int
    open_position_count: int
    max_positions: int


def evaluate_time_rule(
    ctx: RuleContext,
    *,
    enabled: bool = True,
    locked_by_admin: bool = False,
) -> RuleResult:
    """Pass if current_time is within [trading_start, trading_end]."""
    if locked_by_admin:
        return RuleResult(rule_name="time_rule", state=RuleState.LOCKED_BY_ADMIN)
    if not enabled:
        return RuleResult(rule_name="time_rule", state=RuleState.DISABLED)
    now = ctx.current_time
    if ctx.trading_start <= now <= ctx.trading_end:
        elapsed = (now - ctx.trading_start).total_seconds()
        window = (ctx.trading_end - ctx.trading_start).total_seconds()
        remaining = (ctx.trading_end - now).total_seconds()
        return RuleResult(
            rule_name="time_rule",
            state=RuleState.PASS,
            current_value=elapsed,
            threshold_value=window,
            distance_to_trigger=0.0,
        )
    # Before window: distance is seconds until window opens
    if now < ctx.trading_start:
        distance = (ctx.trading_start - now).total_seconds()
    else:
        distance = 0.0
    return RuleResult(
        rule_name="time_rule",
        state=RuleState.FAIL,
        reason=f"current_time {now.isoformat()} outside trading window",
        distance_to_trigger=distance,
    )


def evaluate_price_rule(
    ctx: RuleContext,
    *,
    enabled: bool = True,
    locked_by_admin: bool = False,
) -> RuleResult:
    """Pass if price_min <= current_price <= price_max."""
    if locked_by_admin:
        return RuleResult(rule_name="price_rule", state=RuleState.LOCKED_BY_ADMIN)
    if not enabled:
        return RuleResult(rule_name="price_rule", state=RuleState.DISABLED)
    price = ctx.current_price
    if ctx.price_min <= price <= ctx.price_max:
        return RuleResult(
            rule_name="price_rule",
            state=RuleState.PASS,
            current_value=price,
            threshold_value=ctx.price_max,
            distance_to_trigger=0.0,
        )
    distance = max(ctx.price_min - price, price - ctx.price_max, 0.0)
    return RuleResult(
        rule_name="price_rule",
        state=RuleState.FAIL,
        reason=f"price {price} outside [{ctx.price_min}, {ctx.price_max}]",
        current_value=price,
        threshold_value=ctx.price_max,
        distance_to_trigger=distance,
    )


def evaluate_move_rule(
    ctx: RuleContext,
    *,
    enabled: bool = True,
    locked_by_admin: bool = False,
) -> RuleResult:
    """Pass if abs(current_price - ptb) >= move_threshold.

    move = current_price - ptb (two-directional, absolute numeric only)
    No direction selection. No percent mode.
    """
    if locked_by_admin:
        return RuleResult(rule_name="move_rule", state=RuleState.LOCKED_BY_ADMIN)
    if not enabled:
        return RuleResult(rule_name="move_rule", state=RuleState.DISABLED)
    move = abs(ctx.current_price - ctx.ptb)
    distance = max(ctx.move_threshold - move, 0.0)
    if move >= ctx.move_threshold:
        return RuleResult(
            rule_name="move_rule",
            state=RuleState.PASS,
            current_value=move,
            threshold_value=ctx.move_threshold,
            distance_to_trigger=0.0,
        )
    return RuleResult(
        rule_name="move_rule",
        state=RuleState.FAIL,
        reason=f"abs(move)={move:.4f} < threshold={ctx.move_threshold}",
        current_value=move,
        threshold_value=ctx.move_threshold,
        distance_to_trigger=distance,
    )


def evaluate_spread_rule(
    ctx: RuleContext,
    *,
    enabled: bool = True,
    locked_by_admin: bool = False,
) -> RuleResult:
    """Pass if spread <= spread_max."""
    if locked_by_admin:
        return RuleResult(rule_name="spread_rule", state=RuleState.LOCKED_BY_ADMIN)
    if not enabled:
        return RuleResult(rule_name="spread_rule", state=RuleState.DISABLED)
    spread = ctx.spread
    distance = max(spread - ctx.spread_max, 0.0)
    if spread <= ctx.spread_max:
        return RuleResult(
            rule_name="spread_rule",
            state=RuleState.PASS,
            current_value=spread,
            threshold_value=ctx.spread_max,
            distance_to_trigger=0.0,
        )
    return RuleResult(
        rule_name="spread_rule",
        state=RuleState.FAIL,
        reason=f"spread {spread} > max {ctx.spread_max}",
        current_value=spread,
        threshold_value=ctx.spread_max,
        distance_to_trigger=distance,
    )


def evaluate_event_limit_rule(
    ctx: RuleContext,
    *,
    enabled: bool = True,
    locked_by_admin: bool = False,
) -> RuleResult:
    """Pass if daily_event_count < event_limit."""
    if locked_by_admin:
        return RuleResult(rule_name="event_limit_rule", state=RuleState.LOCKED_BY_ADMIN)
    if not enabled:
        return RuleResult(rule_name="event_limit_rule", state=RuleState.DISABLED)
    count = ctx.daily_event_count
    limit = ctx.event_limit
    distance = max(count - limit + 1, 0.0)
    if count < limit:
        return RuleResult(
            rule_name="event_limit_rule",
            state=RuleState.PASS,
            current_value=float(count),
            threshold_value=float(limit),
            distance_to_trigger=0.0,
        )
    return RuleResult(
        rule_name="event_limit_rule",
        state=RuleState.FAIL,
        reason=f"daily_event_count={count} >= limit={limit}",
        current_value=float(count),
        threshold_value=float(limit),
        distance_to_trigger=float(distance),
    )


def evaluate_max_positions_rule(
    ctx: RuleContext,
    *,
    enabled: bool = True,
    locked_by_admin: bool = False,
) -> RuleResult:
    """Pass if open_position_count < max_positions."""
    if locked_by_admin:
        return RuleResult(rule_name="max_positions_rule", state=RuleState.LOCKED_BY_ADMIN)
    if not enabled:
        return RuleResult(rule_name="max_positions_rule", state=RuleState.DISABLED)
    count = ctx.open_position_count
    limit = ctx.max_positions
    distance = max(count - limit + 1, 0.0)
    if count < limit:
        return RuleResult(
            rule_name="max_positions_rule",
            state=RuleState.PASS,
            current_value=float(count),
            threshold_value=float(limit),
            distance_to_trigger=0.0,
        )
    return RuleResult(
        rule_name="max_positions_rule",
        state=RuleState.FAIL,
        reason=f"open_positions={count} >= max={limit}",
        current_value=float(count),
        threshold_value=float(limit),
        distance_to_trigger=float(distance),
    )
