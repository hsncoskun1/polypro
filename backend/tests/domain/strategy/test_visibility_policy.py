"""Tests for AdminVisibilityPolicy — event/panel/feature visibility."""
import pytest
from app.domain.strategy.visibility_policy import (
    AdminVisibilityPolicy,
    VisibilityEntry,
    VisibilityTargetType,
)


class TestVisibilityTargetType:
    def test_has_event(self):
        assert VisibilityTargetType.EVENT == "event"

    def test_has_panel(self):
        assert VisibilityTargetType.PANEL == "panel"

    def test_has_feature(self):
        assert VisibilityTargetType.FEATURE == "feature"


class TestVisibilityEntry:
    def test_defaults_visible(self):
        entry = VisibilityEntry(
            target_type=VisibilityTargetType.EVENT,
            target_name="market_open",
        )
        assert entry.visible is True

    def test_explicit_hidden(self):
        entry = VisibilityEntry(
            target_type=VisibilityTargetType.PANEL,
            target_name="admin_panel",
            visible=False,
        )
        assert entry.visible is False


class TestAdminVisibilityPolicy:
    def test_unknown_target_defaults_to_visible(self):
        policy = AdminVisibilityPolicy()
        assert policy.is_visible(VisibilityTargetType.EVENT, "anything") is True
        assert policy.is_visible(VisibilityTargetType.PANEL, "anything") is True
        assert policy.is_visible(VisibilityTargetType.FEATURE, "anything") is True

    def test_set_event_hidden(self):
        policy = AdminVisibilityPolicy()
        policy.set_visibility(VisibilityTargetType.EVENT, "market_open", False)
        assert policy.is_visible(VisibilityTargetType.EVENT, "market_open") is False

    def test_set_panel_hidden(self):
        policy = AdminVisibilityPolicy()
        policy.set_visibility(VisibilityTargetType.PANEL, "risk_panel", False)
        assert policy.is_visible(VisibilityTargetType.PANEL, "risk_panel") is False

    def test_set_feature_hidden(self):
        policy = AdminVisibilityPolicy()
        policy.set_visibility(VisibilityTargetType.FEATURE, "advanced_filters", False)
        assert policy.is_visible(VisibilityTargetType.FEATURE, "advanced_filters") is False

    def test_set_visible_explicitly(self):
        policy = AdminVisibilityPolicy()
        policy.set_visibility(VisibilityTargetType.EVENT, "market_close", True)
        assert policy.is_visible(VisibilityTargetType.EVENT, "market_close") is True

    def test_different_types_same_name_independent(self):
        policy = AdminVisibilityPolicy()
        policy.set_visibility(VisibilityTargetType.EVENT, "entry", False)
        assert policy.is_visible(VisibilityTargetType.EVENT, "entry") is False
        assert policy.is_visible(VisibilityTargetType.PANEL, "entry") is True
        assert policy.is_visible(VisibilityTargetType.FEATURE, "entry") is True

    def test_overwrite_visibility(self):
        policy = AdminVisibilityPolicy()
        policy.set_visibility(VisibilityTargetType.PANEL, "summary", False)
        assert policy.is_visible(VisibilityTargetType.PANEL, "summary") is False
        policy.set_visibility(VisibilityTargetType.PANEL, "summary", True)
        assert policy.is_visible(VisibilityTargetType.PANEL, "summary") is True

    def test_empty_policy_default(self):
        policy = AdminVisibilityPolicy()
        assert policy.entries == {}
