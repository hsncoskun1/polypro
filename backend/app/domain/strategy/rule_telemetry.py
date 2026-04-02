"""Rule telemetry/read model.

Represents the visible state of a rule for the user panel.
Combines policy metadata with live rule evaluation results.
"""
from dataclasses import dataclass

from app.domain.strategy.rule_state import RuleState


@dataclass
class RuleTelemetryEntry:
    """Telemetry snapshot for a single rule, ready for user panel display."""
    rule_name: str
    visible: bool
    editable: bool
    enabled: bool
    locked_by_admin: bool
    state: RuleState | None = None
    current_value: float | None = None
    threshold_value: float | None = None
    distance_to_trigger: float | None = None
    reason: str | None = None
