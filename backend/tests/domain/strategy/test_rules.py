from datetime import datetime, timezone

import pytest

from app.domain.strategy.rule_state import RuleState
from app.domain.strategy.rules import (
    RuleContext,
    evaluate_event_limit_rule,
    evaluate_max_positions_rule,
    evaluate_move_rule,
    evaluate_price_rule,
    evaluate_spread_rule,
    evaluate_time_rule,
)

_T_START = datetime(2026, 4, 2, 9, 0, 0, tzinfo=timezone.utc)
_T_END = datetime(2026, 4, 2, 17, 0, 0, tzinfo=timezone.utc)
_T_MID = datetime(2026, 4, 2, 12, 0, 0, tzinfo=timezone.utc)
_T_BEFORE = datetime(2026, 4, 2, 8, 0, 0, tzinfo=timezone.utc)
_T_AFTER = datetime(2026, 4, 2, 18, 0, 0, tzinfo=timezone.utc)


def _ctx(**overrides) -> RuleContext:
    defaults = dict(
        current_price=0.55,
        ptb=0.50,
        spread=0.01,
        current_time=_T_MID,
        trading_start=_T_START,
        trading_end=_T_END,
        move_threshold=0.03,
        price_min=0.10,
        price_max=0.90,
        spread_max=0.05,
        daily_event_count=2,
        event_limit=5,
        open_position_count=1,
        max_positions=3,
    )
    defaults.update(overrides)
    return RuleContext(**defaults)


# ── time_rule ─────────────────────────────────────────────────────────────────

def test_time_rule_pass_during_window():
    result = evaluate_time_rule(_ctx())
    assert result.state == RuleState.PASS


def test_time_rule_fail_before_window():
    result = evaluate_time_rule(_ctx(current_time=_T_BEFORE))
    assert result.state == RuleState.FAIL
    assert result.reason is not None


def test_time_rule_fail_after_window():
    result = evaluate_time_rule(_ctx(current_time=_T_AFTER))
    assert result.state == RuleState.FAIL


def test_time_rule_disabled():
    result = evaluate_time_rule(_ctx(current_time=_T_BEFORE), enabled=False)
    assert result.state == RuleState.DISABLED


def test_time_rule_locked_by_admin():
    result = evaluate_time_rule(_ctx(), locked_by_admin=True)
    assert result.state == RuleState.LOCKED_BY_ADMIN


def test_time_rule_fail_has_distance_to_trigger():
    result = evaluate_time_rule(_ctx(current_time=_T_BEFORE))
    assert result.distance_to_trigger is not None
    assert result.distance_to_trigger > 0


def test_time_rule_pass_has_current_value():
    result = evaluate_time_rule(_ctx())
    assert result.current_value is not None
    assert result.threshold_value is not None


# ── price_rule ────────────────────────────────────────────────────────────────

def test_price_rule_pass_within_range():
    result = evaluate_price_rule(_ctx())
    assert result.state == RuleState.PASS


def test_price_rule_fail_below_min():
    result = evaluate_price_rule(_ctx(current_price=0.05))
    assert result.state == RuleState.FAIL


def test_price_rule_fail_above_max():
    result = evaluate_price_rule(_ctx(current_price=0.95))
    assert result.state == RuleState.FAIL


def test_price_rule_disabled():
    result = evaluate_price_rule(_ctx(current_price=0.05), enabled=False)
    assert result.state == RuleState.DISABLED


def test_price_rule_locked_by_admin():
    result = evaluate_price_rule(_ctx(), locked_by_admin=True)
    assert result.state == RuleState.LOCKED_BY_ADMIN


def test_price_rule_fail_has_current_and_threshold():
    result = evaluate_price_rule(_ctx(current_price=0.05))
    assert result.current_value == 0.05
    assert result.threshold_value is not None
    assert result.distance_to_trigger is not None and result.distance_to_trigger > 0


# ── move_rule ─────────────────────────────────────────────────────────────────

def test_move_rule_pass_when_abs_move_meets_threshold():
    # abs(0.55 - 0.50) = 0.05 >= 0.03
    result = evaluate_move_rule(_ctx())
    assert result.state == RuleState.PASS


def test_move_rule_fail_when_abs_move_below_threshold():
    # abs(0.51 - 0.50) = 0.01 < 0.03
    result = evaluate_move_rule(_ctx(current_price=0.51))
    assert result.state == RuleState.FAIL
    assert result.reason is not None


def test_move_rule_pass_negative_direction():
    # abs(0.45 - 0.50) = 0.05 >= 0.03 — no direction filter
    result = evaluate_move_rule(_ctx(current_price=0.45))
    assert result.state == RuleState.PASS


def test_move_rule_disabled():
    result = evaluate_move_rule(_ctx(current_price=0.51), enabled=False)
    assert result.state == RuleState.DISABLED


def test_move_rule_locked_by_admin():
    result = evaluate_move_rule(_ctx(), locked_by_admin=True)
    assert result.state == RuleState.LOCKED_BY_ADMIN


def test_move_rule_exact_threshold_passes():
    # abs(0.53 - 0.50) = 0.03 == 0.03 — boundary is inclusive
    result = evaluate_move_rule(_ctx(current_price=0.53))
    assert result.state == RuleState.PASS


def test_move_rule_fail_has_current_value_and_distance():
    result = evaluate_move_rule(_ctx(current_price=0.51))
    assert result.current_value is not None
    assert result.threshold_value == 0.03
    assert result.distance_to_trigger is not None and result.distance_to_trigger > 0


def test_move_rule_pass_has_distance_to_trigger_zero():
    result = evaluate_move_rule(_ctx())
    assert result.distance_to_trigger == 0.0


# ── spread_rule ───────────────────────────────────────────────────────────────

def test_spread_rule_pass():
    result = evaluate_spread_rule(_ctx())
    assert result.state == RuleState.PASS


def test_spread_rule_fail_exceeds_max():
    result = evaluate_spread_rule(_ctx(spread=0.10))
    assert result.state == RuleState.FAIL


def test_spread_rule_disabled():
    result = evaluate_spread_rule(_ctx(spread=0.10), enabled=False)
    assert result.state == RuleState.DISABLED


def test_spread_rule_locked_by_admin():
    result = evaluate_spread_rule(_ctx(), locked_by_admin=True)
    assert result.state == RuleState.LOCKED_BY_ADMIN


def test_spread_rule_fail_has_distance_to_trigger():
    result = evaluate_spread_rule(_ctx(spread=0.10))
    assert result.distance_to_trigger is not None and result.distance_to_trigger > 0


# ── event_limit_rule ──────────────────────────────────────────────────────────

def test_event_limit_rule_pass():
    result = evaluate_event_limit_rule(_ctx())
    assert result.state == RuleState.PASS


def test_event_limit_rule_fail_at_limit():
    result = evaluate_event_limit_rule(_ctx(daily_event_count=5, event_limit=5))
    assert result.state == RuleState.FAIL


def test_event_limit_rule_disabled():
    result = evaluate_event_limit_rule(_ctx(daily_event_count=10), enabled=False)
    assert result.state == RuleState.DISABLED


def test_event_limit_rule_locked_by_admin():
    result = evaluate_event_limit_rule(_ctx(), locked_by_admin=True)
    assert result.state == RuleState.LOCKED_BY_ADMIN


def test_event_limit_rule_has_current_and_threshold():
    result = evaluate_event_limit_rule(_ctx())
    assert result.current_value == 2.0
    assert result.threshold_value == 5.0


# ── max_positions_rule ────────────────────────────────────────────────────────

def test_max_positions_rule_pass():
    result = evaluate_max_positions_rule(_ctx())
    assert result.state == RuleState.PASS


def test_max_positions_rule_fail_at_max():
    result = evaluate_max_positions_rule(_ctx(open_position_count=3, max_positions=3))
    assert result.state == RuleState.FAIL


def test_max_positions_rule_disabled():
    result = evaluate_max_positions_rule(_ctx(open_position_count=99), enabled=False)
    assert result.state == RuleState.DISABLED


def test_max_positions_rule_locked_by_admin():
    result = evaluate_max_positions_rule(_ctx(), locked_by_admin=True)
    assert result.state == RuleState.LOCKED_BY_ADMIN


def test_max_positions_rule_has_current_and_threshold():
    result = evaluate_max_positions_rule(_ctx())
    assert result.current_value == 1.0
    assert result.threshold_value == 3.0
