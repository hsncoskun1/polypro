"""Trading entry decision engine.

Evaluates all entry rules against a RuleContext and produces an EntryDecision.
trade_allowed is True only when ALL enabled, non-locked rules pass.
Disabled and locked_by_admin rules are excluded from the pass/fail count.
"""
from dataclasses import dataclass

from app.domain.strategy.entry_decision import EntryDecision
from app.domain.strategy.rule_result import RuleResult
from app.domain.strategy.rule_state import RuleState
from app.domain.strategy.rules import (
    RuleContext,
    evaluate_event_limit_rule,
    evaluate_max_positions_rule,
    evaluate_move_rule,
    evaluate_price_rule,
    evaluate_spread_rule,
    evaluate_time_rule,
)


@dataclass
class RuleConfig:
    """Toggles and admin locks for each entry rule. All enabled by default."""
    time_rule: bool = True
    price_rule: bool = True
    move_rule: bool = True
    spread_rule: bool = True
    event_limit_rule: bool = True
    max_positions_rule: bool = True

    # Admin locks — reserved for v0.4.1 governance layer
    time_rule_locked_by_admin: bool = False
    price_rule_locked_by_admin: bool = False
    move_rule_locked_by_admin: bool = False
    spread_rule_locked_by_admin: bool = False
    event_limit_rule_locked_by_admin: bool = False
    max_positions_rule_locked_by_admin: bool = False


_BLOCKING_STATES = {RuleState.FAIL}


def evaluate_entry(ctx: RuleContext, config: RuleConfig | None = None) -> EntryDecision:
    """Run all entry rules and return an EntryDecision.

    A rule that is disabled or locked_by_admin is excluded from the blocking set.
    Any single FAIL among active rules blocks the trade.
    """
    if config is None:
        config = RuleConfig()

    results: list[RuleResult] = [
        evaluate_time_rule(
            ctx,
            enabled=config.time_rule,
            locked_by_admin=config.time_rule_locked_by_admin,
        ),
        evaluate_price_rule(
            ctx,
            enabled=config.price_rule,
            locked_by_admin=config.price_rule_locked_by_admin,
        ),
        evaluate_move_rule(
            ctx,
            enabled=config.move_rule,
            locked_by_admin=config.move_rule_locked_by_admin,
        ),
        evaluate_spread_rule(
            ctx,
            enabled=config.spread_rule,
            locked_by_admin=config.spread_rule_locked_by_admin,
        ),
        evaluate_event_limit_rule(
            ctx,
            enabled=config.event_limit_rule,
            locked_by_admin=config.event_limit_rule_locked_by_admin,
        ),
        evaluate_max_positions_rule(
            ctx,
            enabled=config.max_positions_rule,
            locked_by_admin=config.max_positions_rule_locked_by_admin,
        ),
    ]

    blocking = [r for r in results if r.state in _BLOCKING_STATES]

    if blocking:
        reasons = "; ".join(r.reason or r.rule_name for r in blocking)
        return EntryDecision(trade_allowed=False, rule_results=results, reason=reasons)

    return EntryDecision(trade_allowed=True, rule_results=results)
