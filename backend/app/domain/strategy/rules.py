"""Entry rule evaluators for the trading decision engine.

Each rule takes a RuleContext and returns a RuleResult.
Disabled rules return RuleState.DISABLED and are never counted as PASS.
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


def evaluate_time_rule(ctx: RuleContext, *, enabled: bool = True) -> RuleResult:
    """Pass if current_time is within [trading_start, trading_end]."""
    if not enabled:
        return RuleResult(rule_name="time_rule", state=RuleState.DISABLED)
    now = ctx.current_time
    if ctx.trading_start <= now <= ctx.trading_end:
        return RuleResult(rule_name="time_rule", state=RuleState.PASS)
    return RuleResult(
        rule_name="time_rule",
        state=RuleState.FAIL,
        reason=f"current_time {now.isoformat()} outside trading window",
    )


def evaluate_price_rule(ctx: RuleContext, *, enabled: bool = True) -> RuleResult:
    """Pass if price_min <= current_price <= price_max."""
    if not enabled:
        return RuleResult(rule_name="price_rule", state=RuleState.DISABLED)
    if ctx.price_min <= ctx.current_price <= ctx.price_max:
        return RuleResult(rule_name="price_rule", state=RuleState.PASS)
    return RuleResult(
        rule_name="price_rule",
        state=RuleState.FAIL,
        reason=f"price {ctx.current_price} outside [{ctx.price_min}, {ctx.price_max}]",
    )


def evaluate_move_rule(ctx: RuleContext, *, enabled: bool = True) -> RuleResult:
    """Pass if abs(current_price - ptb) >= move_threshold.

    move = current_price - ptb (two-directional, absolute numeric only)
    No direction selection. No percent mode.
    """
    if not enabled:
        return RuleResult(rule_name="move_rule", state=RuleState.DISABLED)
    move = abs(ctx.current_price - ctx.ptb)
    if move >= ctx.move_threshold:
        return RuleResult(rule_name="move_rule", state=RuleState.PASS)
    return RuleResult(
        rule_name="move_rule",
        state=RuleState.FAIL,
        reason=f"abs(move)={move:.4f} < threshold={ctx.move_threshold}",
    )


def evaluate_spread_rule(ctx: RuleContext, *, enabled: bool = True) -> RuleResult:
    """Pass if spread <= spread_max."""
    if not enabled:
        return RuleResult(rule_name="spread_rule", state=RuleState.DISABLED)
    if ctx.spread <= ctx.spread_max:
        return RuleResult(rule_name="spread_rule", state=RuleState.PASS)
    return RuleResult(
        rule_name="spread_rule",
        state=RuleState.FAIL,
        reason=f"spread {ctx.spread} > max {ctx.spread_max}",
    )


def evaluate_event_limit_rule(ctx: RuleContext, *, enabled: bool = True) -> RuleResult:
    """Pass if daily_event_count < event_limit."""
    if not enabled:
        return RuleResult(rule_name="event_limit_rule", state=RuleState.DISABLED)
    if ctx.daily_event_count < ctx.event_limit:
        return RuleResult(rule_name="event_limit_rule", state=RuleState.PASS)
    return RuleResult(
        rule_name="event_limit_rule",
        state=RuleState.FAIL,
        reason=f"daily_event_count={ctx.daily_event_count} >= limit={ctx.event_limit}",
    )


def evaluate_max_positions_rule(ctx: RuleContext, *, enabled: bool = True) -> RuleResult:
    """Pass if open_position_count < max_positions."""
    if not enabled:
        return RuleResult(rule_name="max_positions_rule", state=RuleState.DISABLED)
    if ctx.open_position_count < ctx.max_positions:
        return RuleResult(rule_name="max_positions_rule", state=RuleState.PASS)
    return RuleResult(
        rule_name="max_positions_rule",
        state=RuleState.FAIL,
        reason=f"open_positions={ctx.open_position_count} >= max={ctx.max_positions}",
    )
