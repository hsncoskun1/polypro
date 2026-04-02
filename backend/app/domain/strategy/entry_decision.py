from dataclasses import dataclass, field

from app.domain.strategy.rule_result import RuleResult


@dataclass
class EntryDecision:
    trade_allowed: bool
    rule_results: list[RuleResult] = field(default_factory=list)
    reason: str | None = None
