"""Trading entry decision engine.

Evaluates all entry rules against a RuleContext and produces an EntryDecision.
trade_allowed is True only when ALL enabled rules pass.
Disabled rules are excluded from the pass/fail count.
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
    """Toggles for each entry rule. All enabled by default."""
    time_rule: bool = True
    price_rule: bool = True
    move_rule: bool = True
    spread_rule: bool = True
    event_limit_rule: bool = True
    max_positions_rule: bool = True


def evaluate_entry(ctx: RuleContext, config: RuleConfig | None = None) -> EntryDecision:
    """Run all entry rules and return an EntryDecision.

    A rule that is disabled is excluded from the blocking set.
    Any single FAIL among enabled rules blocks the trade.
    """
    if config is None:
        config = RuleConfig()

    results: list[RuleResult] = [
        evaluate_time_rule(ctx, enabled=config.time_rule),
        evaluate_price_rule(ctx, enabled=config.price_rule),
        evaluate_move_rule(ctx, enabled=config.move_rule),
        evaluate_spread_rule(ctx, enabled=config.spread_rule),
        evaluate_event_limit_rule(ctx, enabled=config.event_limit_rule),
        evaluate_max_positions_rule(ctx, enabled=config.max_positions_rule),
    ]

    blocking = [r for r in results if r.state == RuleState.FAIL]

    if blocking:
        reasons = "; ".join(r.reason or r.rule_name for r in blocking)
        return EntryDecision(trade_allowed=False, rule_results=results, reason=reasons)

    return EntryDecision(trade_allowed=True, rule_results=results)
