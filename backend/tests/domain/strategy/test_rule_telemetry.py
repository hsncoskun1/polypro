"""Tests for RuleTelemetryEntry model."""
from app.domain.strategy.rule_state import RuleState
from app.domain.strategy.rule_telemetry import RuleTelemetryEntry


class TestRuleTelemetryEntry:
    def test_required_fields(self):
        entry = RuleTelemetryEntry(
            rule_name="time_rule",
            visible=True,
            editable=True,
            enabled=True,
            locked_by_admin=False,
        )
        assert entry.rule_name == "time_rule"
        assert entry.visible is True
        assert entry.editable is True
        assert entry.enabled is True
        assert entry.locked_by_admin is False

    def test_optional_fields_default_to_none(self):
        entry = RuleTelemetryEntry(
            rule_name="price_rule",
            visible=True,
            editable=False,
            enabled=True,
            locked_by_admin=True,
        )
        assert entry.state is None
        assert entry.current_value is None
        assert entry.threshold_value is None
        assert entry.distance_to_trigger is None
        assert entry.reason is None

    def test_with_all_fields(self):
        entry = RuleTelemetryEntry(
            rule_name="move_rule",
            visible=True,
            editable=True,
            enabled=True,
            locked_by_admin=False,
            state=RuleState.FAIL,
            current_value=0.05,
            threshold_value=0.1,
            distance_to_trigger=0.05,
            reason="move below threshold",
        )
        assert entry.state == RuleState.FAIL
        assert entry.current_value == 0.05
        assert entry.threshold_value == 0.1
        assert entry.distance_to_trigger == 0.05
        assert entry.reason == "move below threshold"

    def test_hidden_non_editable_locked(self):
        entry = RuleTelemetryEntry(
            rule_name="spread_rule",
            visible=False,
            editable=False,
            enabled=False,
            locked_by_admin=True,
        )
        assert entry.visible is False
        assert entry.editable is False
        assert entry.locked_by_admin is True
