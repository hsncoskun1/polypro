from dataclasses import dataclass

from app.domain.strategy.rule_state import RuleState


@dataclass
class RuleResult:
    rule_name: str
    state: RuleState
    reason: str | None = None
