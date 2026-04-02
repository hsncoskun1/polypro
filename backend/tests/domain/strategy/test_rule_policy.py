"""Tests for RulePolicyEntry, AdminRulePolicy, and UserRuleSelection models."""
import pytest
from app.domain.strategy.rule_policy import AdminRulePolicy, RulePolicyEntry
from app.domain.strategy.user_rule_selection import UserRuleSelection


class TestRulePolicyEntry:
    def test_defaults(self):
        entry = RulePolicyEntry(rule_name="time_rule")
        assert entry.available is True
        assert entry.visible is True
        assert entry.editable is True
        assert entry.required is False
        assert entry.locked_by_admin is False
        assert entry.default_enabled is True

    def test_required_non_editable_entry(self):
        entry = RulePolicyEntry(rule_name="spread_rule", required=True, editable=False)
        assert entry.required is True
        assert entry.editable is False

    def test_unavailable_entry(self):
        entry = RulePolicyEntry(rule_name="move_rule", available=False)
        assert entry.available is False

    def test_locked_entry(self):
        entry = RulePolicyEntry(rule_name="price_rule", locked_by_admin=True)
        assert entry.locked_by_admin is True


class TestAdminRulePolicy:
    def test_defaults(self):
        policy = AdminRulePolicy()
        assert policy.rules == {}
        assert policy.min_active_rules == 0
        assert policy.max_active_rules == 6

    def test_with_rules(self):
        entry = RulePolicyEntry(rule_name="time_rule")
        policy = AdminRulePolicy(rules={"time_rule": entry})
        assert "time_rule" in policy.rules

    def test_min_max_configurable(self):
        policy = AdminRulePolicy(min_active_rules=2, max_active_rules=4)
        assert policy.min_active_rules == 2
        assert policy.max_active_rules == 4


class TestUserRuleSelection:
    def test_empty_by_default(self):
        sel = UserRuleSelection()
        assert sel.enabled_rules == set()

    def test_with_rules(self):
        sel = UserRuleSelection(enabled_rules={"time_rule", "price_rule"})
        assert "time_rule" in sel.enabled_rules
        assert "price_rule" in sel.enabled_rules
        assert "move_rule" not in sel.enabled_rules
