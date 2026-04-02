"""User rule selection model.

Represents the set of rules a user has chosen to enable.
Only rules permitted by AdminRulePolicy can be included.
"""
from dataclasses import dataclass, field


@dataclass
class UserRuleSelection:
    """Which rules the user has enabled."""
    enabled_rules: set[str] = field(default_factory=set)
