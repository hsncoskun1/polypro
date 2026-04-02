"""Rule governance layer.

Applies AdminRulePolicy + UserRuleSelection to produce a validated RuleConfig
and user-facing telemetry. Runtime state is never directly edited here — only
config is derived from policy.
"""
from __future__ import annotations

from app.domain.strategy.entry_decision import EntryDecision
from app.domain.strategy.rule_policy import AdminRulePolicy
from app.domain.strategy.rule_result import RuleResult
from app.domain.strategy.rule_telemetry import RuleTelemetryEntry
from app.domain.strategy.strategy import RuleConfig
from app.domain.strategy.user_rule_selection import UserRuleSelection

RULE_NAMES = [
    "time_rule",
    "price_rule",
    "move_rule",
    "spread_rule",
    "event_limit_rule",
    "max_positions_rule",
]


def validate_user_selection(
    policy: AdminRulePolicy,
    selection: UserRuleSelection,
) -> None:
    """Raise ValueError if selection violates policy constraints.

    Checks:
    - required rules must remain enabled
    - active rule count is within [min_active_rules, max_active_rules]
    """
    for rule_name, entry in policy.rules.items():
        if entry.required and rule_name not in selection.enabled_rules:
            raise ValueError(
                f"Rule '{rule_name}' is required and cannot be disabled."
            )

    active_count = _count_active(policy, selection)

    if active_count < policy.min_active_rules:
        raise ValueError(
            f"Active rules ({active_count}) is below minimum ({policy.min_active_rules})."
        )
    if active_count > policy.max_active_rules:
        raise ValueError(
            f"Active rules ({active_count}) exceeds maximum ({policy.max_active_rules})."
        )


def build_rule_config(
    policy: AdminRulePolicy,
    selection: UserRuleSelection,
) -> RuleConfig:
    """Build a RuleConfig by applying policy + user selection.

    - Unavailable rules → disabled
    - Non-editable rules → policy default_enabled (user selection ignored)
    - Required rules → always enabled regardless of user selection
    - All others → user selection applies
    - locked_by_admin propagated from policy entry
    """
    kwargs: dict[str, bool] = {}
    for rule_name in RULE_NAMES:
        entry = policy.rules.get(rule_name)
        if entry is None or not entry.available:
            kwargs[rule_name] = False
            kwargs[f"{rule_name}_locked_by_admin"] = False
        elif not entry.editable:
            kwargs[rule_name] = entry.default_enabled
            kwargs[f"{rule_name}_locked_by_admin"] = entry.locked_by_admin
        else:
            enabled = rule_name in selection.enabled_rules
            if entry.required:
                enabled = True
            kwargs[rule_name] = enabled
            kwargs[f"{rule_name}_locked_by_admin"] = entry.locked_by_admin

    return RuleConfig(**kwargs)


def build_telemetry(
    policy: AdminRulePolicy,
    selection: UserRuleSelection,
    decision: EntryDecision | None = None,
) -> list[RuleTelemetryEntry]:
    """Build telemetry entries for all visible rules.

    Hidden rules (visible=False) are excluded entirely.
    State/value fields are populated from EntryDecision when provided.
    """
    result_map: dict[str, RuleResult] = {}
    if decision is not None:
        for r in decision.rule_results:
            result_map[r.rule_name] = r

    entries: list[RuleTelemetryEntry] = []
    for rule_name in RULE_NAMES:
        entry = policy.rules.get(rule_name)
        if entry is None or not entry.visible:
            continue

        if not entry.editable:
            enabled = entry.default_enabled
        else:
            enabled = rule_name in selection.enabled_rules

        if entry.required:
            enabled = True

        rule_result = result_map.get(rule_name)

        entries.append(RuleTelemetryEntry(
            rule_name=rule_name,
            visible=entry.visible,
            editable=entry.editable,
            enabled=enabled,
            locked_by_admin=entry.locked_by_admin,
            state=rule_result.state if rule_result else None,
            current_value=rule_result.current_value if rule_result else None,
            threshold_value=rule_result.threshold_value if rule_result else None,
            distance_to_trigger=rule_result.distance_to_trigger if rule_result else None,
            reason=rule_result.reason if rule_result else None,
        ))

    return entries


# ── internal helpers ──────────────────────────────────────────────────────────

def _count_active(policy: AdminRulePolicy, selection: UserRuleSelection) -> int:
    """Count rules that will be active given policy + selection."""
    count = 0
    for rule_name in RULE_NAMES:
        entry = policy.rules.get(rule_name)
        if entry is None or not entry.available:
            continue
        if not entry.editable:
            if entry.default_enabled:
                count += 1
        else:
            if entry.required or rule_name in selection.enabled_rules:
                count += 1
    return count
