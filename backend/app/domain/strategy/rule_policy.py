"""Admin rule policy model.

Defines which rules are available, visible, editable, required, or locked.
Admin controls this policy; users interact only within what policy permits.
"""
from dataclasses import dataclass, field


@dataclass
class RulePolicyEntry:
    """Policy settings for a single rule."""
    rule_name: str
    available: bool = True          # rule exists in system (admin makes it available)
    visible: bool = True            # visible in user panel
    editable: bool = True           # user can toggle enabled state
    required: bool = False          # user cannot disable (always enabled)
    locked_by_admin: bool = False   # governance lock seam (v0.4.0 semantics)
    default_enabled: bool = True    # authoritative state for non-editable rules


@dataclass
class AdminRulePolicy:
    """Full admin policy across all rules."""
    rules: dict[str, RulePolicyEntry] = field(default_factory=dict)
    min_active_rules: int = 0
    max_active_rules: int = 6
