"""Tests for governance layer: validate_user_selection, build_rule_config, build_telemetry."""
import pytest
from app.domain.strategy.governance import (
    build_rule_config,
    build_telemetry,
    validate_user_selection,
)
from app.domain.strategy.rule_policy import AdminRulePolicy, RulePolicyEntry
from app.domain.strategy.rule_result import RuleResult
from app.domain.strategy.rule_state import RuleState
from app.domain.strategy.entry_decision import EntryDecision
from app.domain.strategy.user_rule_selection import UserRuleSelection


def _full_policy(**overrides) -> AdminRulePolicy:
    """Build a policy with all 6 rules available/visible/editable by default."""
    rule_names = [
        "time_rule", "price_rule", "move_rule",
        "spread_rule", "event_limit_rule", "max_positions_rule",
    ]
    rules = {
        name: RulePolicyEntry(rule_name=name, **overrides.get(name, {}))
        for name in rule_names
    }
    return AdminRulePolicy(rules=rules)


def _all_enabled() -> UserRuleSelection:
    return UserRuleSelection(enabled_rules={
        "time_rule", "price_rule", "move_rule",
        "spread_rule", "event_limit_rule", "max_positions_rule",
    })


# ── validate_user_selection ───────────────────────────────────────────────────

class TestValidateUserSelection:
    def test_required_rule_cannot_be_disabled(self):
        policy = _full_policy(time_rule={"required": True})
        selection = UserRuleSelection(enabled_rules={"price_rule"})
        with pytest.raises(ValueError, match="time_rule.*required"):
            validate_user_selection(policy, selection)

    def test_required_rule_enabled_passes(self):
        policy = _full_policy(time_rule={"required": True})
        selection = UserRuleSelection(enabled_rules={"time_rule", "price_rule"})
        validate_user_selection(policy, selection)  # no error

    def test_below_min_active_rules_raises(self):
        policy = _full_policy()
        policy.min_active_rules = 3
        selection = UserRuleSelection(enabled_rules={"time_rule", "price_rule"})
        with pytest.raises(ValueError, match="minimum"):
            validate_user_selection(policy, selection)

    def test_above_max_active_rules_raises(self):
        policy = _full_policy()
        policy.max_active_rules = 2
        selection = _all_enabled()
        with pytest.raises(ValueError, match="maximum"):
            validate_user_selection(policy, selection)

    def test_valid_selection_passes(self):
        policy = _full_policy()
        selection = UserRuleSelection(enabled_rules={"time_rule", "price_rule", "move_rule"})
        validate_user_selection(policy, selection)  # no error

    def test_empty_selection_valid_when_no_min(self):
        policy = _full_policy()
        policy.min_active_rules = 0
        selection = UserRuleSelection()
        validate_user_selection(policy, selection)  # no error

    def test_non_editable_rule_uses_policy_default_in_count(self):
        """Non-editable default_enabled=True rule counts as active regardless of user selection."""
        policy = _full_policy(time_rule={"editable": False, "default_enabled": True})
        policy.min_active_rules = 1
        selection = UserRuleSelection()  # user selects nothing
        validate_user_selection(policy, selection)  # time_rule counts as active via policy


# ── build_rule_config ─────────────────────────────────────────────────────────

class TestBuildRuleConfig:
    def test_user_enabled_rules_reflected(self):
        policy = _full_policy()
        selection = UserRuleSelection(enabled_rules={"time_rule", "price_rule"})
        config = build_rule_config(policy, selection)
        assert config.time_rule is True
        assert config.price_rule is True
        assert config.move_rule is False
        assert config.spread_rule is False

    def test_non_editable_uses_policy_default_not_user_selection(self):
        policy = _full_policy(
            time_rule={"editable": False, "default_enabled": False}
        )
        selection = UserRuleSelection(enabled_rules={"time_rule"})  # user tries to enable
        config = build_rule_config(policy, selection)
        assert config.time_rule is False  # policy default wins

    def test_required_always_enabled_regardless_of_selection(self):
        policy = _full_policy(spread_rule={"required": True})
        selection = UserRuleSelection()  # user doesn't include spread_rule
        config = build_rule_config(policy, selection)
        assert config.spread_rule is True

    def test_unavailable_rule_disabled(self):
        policy = _full_policy(move_rule={"available": False})
        selection = _all_enabled()
        config = build_rule_config(policy, selection)
        assert config.move_rule is False
        assert config.move_rule_locked_by_admin is False

    def test_locked_by_admin_propagated(self):
        policy = _full_policy(price_rule={"locked_by_admin": True})
        selection = _all_enabled()
        config = build_rule_config(policy, selection)
        assert config.price_rule_locked_by_admin is True

    def test_no_policy_entry_disables_rule(self):
        policy = AdminRulePolicy(rules={})  # empty policy
        selection = _all_enabled()
        config = build_rule_config(policy, selection)
        assert config.time_rule is False
        assert config.price_rule is False


# ── build_telemetry ───────────────────────────────────────────────────────────

class TestBuildTelemetry:
    def test_hidden_rule_excluded_from_telemetry(self):
        policy = _full_policy(time_rule={"visible": False})
        selection = _all_enabled()
        entries = build_telemetry(policy, selection)
        names = [e.rule_name for e in entries]
        assert "time_rule" not in names

    def test_visible_rules_included(self):
        policy = _full_policy()
        selection = _all_enabled()
        entries = build_telemetry(policy, selection)
        names = [e.rule_name for e in entries]
        for rule in ["time_rule", "price_rule", "move_rule",
                     "spread_rule", "event_limit_rule", "max_positions_rule"]:
            assert rule in names

    def test_telemetry_carries_all_fields(self):
        policy = _full_policy()
        selection = _all_enabled()
        entries = build_telemetry(policy, selection)
        entry = entries[0]
        assert hasattr(entry, "rule_name")
        assert hasattr(entry, "visible")
        assert hasattr(entry, "editable")
        assert hasattr(entry, "enabled")
        assert hasattr(entry, "locked_by_admin")
        assert hasattr(entry, "state")
        assert hasattr(entry, "current_value")
        assert hasattr(entry, "threshold_value")
        assert hasattr(entry, "distance_to_trigger")
        assert hasattr(entry, "reason")

    def test_no_decision_state_is_none(self):
        policy = _full_policy()
        selection = _all_enabled()
        entries = build_telemetry(policy, selection, decision=None)
        for e in entries:
            assert e.state is None
            assert e.current_value is None

    def test_with_decision_populates_state_and_values(self):
        policy = _full_policy()
        selection = _all_enabled()
        rule_result = RuleResult(
            rule_name="time_rule",
            state=RuleState.PASS,
            current_value=0.5,
            threshold_value=0.2,
            distance_to_trigger=0.0,
        )
        decision = EntryDecision(trade_allowed=True, rule_results=[rule_result])
        entries = build_telemetry(policy, selection, decision=decision)
        time_entry = next(e for e in entries if e.rule_name == "time_rule")
        assert time_entry.state == RuleState.PASS
        assert time_entry.current_value == 0.5
        assert time_entry.threshold_value == 0.2
        assert time_entry.distance_to_trigger == 0.0

    def test_locked_by_admin_reflected_in_telemetry(self):
        policy = _full_policy(price_rule={"locked_by_admin": True})
        selection = _all_enabled()
        entries = build_telemetry(policy, selection)
        price_entry = next(e for e in entries if e.rule_name == "price_rule")
        assert price_entry.locked_by_admin is True

    def test_non_editable_rule_enabled_reflects_policy_default(self):
        policy = _full_policy(move_rule={"editable": False, "default_enabled": False})
        selection = UserRuleSelection(enabled_rules={"move_rule"})  # user tries to enable
        entries = build_telemetry(policy, selection)
        move_entry = next(e for e in entries if e.rule_name == "move_rule")
        assert move_entry.enabled is False  # policy wins
        assert move_entry.editable is False

    def test_required_rule_always_enabled_in_telemetry(self):
        policy = _full_policy(spread_rule={"required": True})
        selection = UserRuleSelection()  # user doesn't include it
        entries = build_telemetry(policy, selection)
        spread_entry = next(e for e in entries if e.rule_name == "spread_rule")
        assert spread_entry.enabled is True
