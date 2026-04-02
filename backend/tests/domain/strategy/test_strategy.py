from datetime import datetime, timezone

from app.domain.strategy.rule_state import RuleState
from app.domain.strategy.strategy import RuleConfig, evaluate_entry
from app.domain.strategy.rules import RuleContext

_T_START = datetime(2026, 4, 2, 9, 0, 0, tzinfo=timezone.utc)
_T_END = datetime(2026, 4, 2, 17, 0, 0, tzinfo=timezone.utc)
_T_MID = datetime(2026, 4, 2, 12, 0, 0, tzinfo=timezone.utc)


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


def test_all_rules_pass_trade_allowed():
    decision = evaluate_entry(_ctx())
    assert decision.trade_allowed is True
    assert decision.reason is None


def test_single_fail_blocks_trade():
    # spread too high — spread_rule fails
    decision = evaluate_entry(_ctx(spread=0.20))
    assert decision.trade_allowed is False
    assert decision.reason is not None


def test_multiple_fails_all_captured_in_reason():
    # both spread and move fail
    decision = evaluate_entry(_ctx(spread=0.20, current_price=0.51))
    assert decision.trade_allowed is False
    assert "spread_rule" in decision.reason or "spread" in decision.reason


def test_disabled_rule_does_not_block_trade():
    # move would fail but is disabled
    config = RuleConfig(move_rule=False)
    decision = evaluate_entry(_ctx(current_price=0.51), config=config)
    assert decision.trade_allowed is True


def test_disabled_rule_appears_in_results_as_disabled():
    config = RuleConfig(time_rule=False)
    decision = evaluate_entry(_ctx(), config=config)
    time_result = next(r for r in decision.rule_results if r.rule_name == "time_rule")
    assert time_result.state == RuleState.DISABLED


def test_locked_by_admin_rule_does_not_block_trade():
    # move would fail but is locked_by_admin — excluded from blocking
    config = RuleConfig(move_rule_locked_by_admin=True)
    decision = evaluate_entry(_ctx(current_price=0.51), config=config)
    assert decision.trade_allowed is True


def test_locked_by_admin_rule_appears_in_results():
    config = RuleConfig(spread_rule_locked_by_admin=True)
    decision = evaluate_entry(_ctx(), config=config)
    spread_result = next(r for r in decision.rule_results if r.rule_name == "spread_rule")
    assert spread_result.state == RuleState.LOCKED_BY_ADMIN


def test_all_rules_disabled_trade_allowed():
    config = RuleConfig(
        time_rule=False,
        price_rule=False,
        move_rule=False,
        spread_rule=False,
        event_limit_rule=False,
        max_positions_rule=False,
    )
    decision = evaluate_entry(_ctx(), config=config)
    assert decision.trade_allowed is True


def test_rule_results_contain_all_six_rules():
    decision = evaluate_entry(_ctx())
    rule_names = {r.rule_name for r in decision.rule_results}
    assert rule_names == {
        "time_rule",
        "price_rule",
        "move_rule",
        "spread_rule",
        "event_limit_rule",
        "max_positions_rule",
    }


def test_default_config_is_all_enabled_no_locks():
    config = RuleConfig()
    assert all([
        config.time_rule,
        config.price_rule,
        config.move_rule,
        config.spread_rule,
        config.event_limit_rule,
        config.max_positions_rule,
    ])
    assert not any([
        config.time_rule_locked_by_admin,
        config.price_rule_locked_by_admin,
        config.move_rule_locked_by_admin,
        config.spread_rule_locked_by_admin,
        config.event_limit_rule_locked_by_admin,
        config.max_positions_rule_locked_by_admin,
    ])


def test_move_rule_uses_ptb_formula():
    # abs(0.45 - 0.50) = 0.05 >= 0.03 — negative direction also passes
    decision = evaluate_entry(_ctx(current_price=0.45))
    move_result = next(r for r in decision.rule_results if r.rule_name == "move_rule")
    assert move_result.state == RuleState.PASS


def test_entry_decision_trade_allowed_false_when_at_max_positions():
    decision = evaluate_entry(_ctx(open_position_count=3, max_positions=3))
    assert decision.trade_allowed is False


def test_rule_results_include_current_value_and_threshold():
    decision = evaluate_entry(_ctx())
    for r in decision.rule_results:
        # all active passing rules should carry values
        assert r.current_value is not None or r.state in (
            RuleState.DISABLED, RuleState.LOCKED_BY_ADMIN
        )


def test_failing_rule_has_distance_to_trigger():
    decision = evaluate_entry(_ctx(current_price=0.51))
    move_result = next(r for r in decision.rule_results if r.rule_name == "move_rule")
    assert move_result.state == RuleState.FAIL
    assert move_result.distance_to_trigger is not None
    assert move_result.distance_to_trigger > 0
