"""Tests for risk engine evaluation — v0.6.0."""
from app.domain.risk.risk_context import RiskContext
from app.domain.risk.risk_result import RiskResult
from app.domain.risk.risk_evaluator import evaluate_risk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clear_ctx(**overrides) -> RiskContext:
    """Base context where all constraints are comfortably within limits."""
    defaults = dict(
        daily_loss_limit=100.0,
        current_daily_loss=0.0,
        daily_trade_cap=10,
        current_daily_trade_count=0,
        event_limit=3,
        current_event_open_positions=0,
        max_concurrent_positions=5,
        current_open_positions=0,
        min_position_size=1.0,
        max_position_size=500.0,
        requested_position_size=10.0,
    )
    defaults.update(overrides)
    return RiskContext(**defaults)


# ---------------------------------------------------------------------------
# TestRiskResult
# ---------------------------------------------------------------------------

class TestRiskResult:
    def test_allowed_result_fields(self):
        result = RiskResult(risk_allowed=True, blocker_reasons=[])
        assert result.risk_allowed is True
        assert result.blocker_reasons == []

    def test_blocked_result_fields(self):
        result = RiskResult(risk_allowed=False, blocker_reasons=["daily_loss_limit_exceeded"])
        assert result.risk_allowed is False
        assert "daily_loss_limit_exceeded" in result.blocker_reasons

    def test_blocker_reasons_default_empty(self):
        result = RiskResult(risk_allowed=True)
        assert result.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestAllClear
# ---------------------------------------------------------------------------

class TestAllClear:
    def test_all_clear_returns_allowed(self):
        result = evaluate_risk(clear_ctx())
        assert result.risk_allowed is True
        assert result.blocker_reasons == []

    def test_well_within_limits_allowed(self):
        ctx = clear_ctx(
            current_daily_loss=10.0,
            current_daily_trade_count=3,
            current_event_open_positions=1,
            current_open_positions=2,
            requested_position_size=25.0,
        )
        result = evaluate_risk(ctx)
        assert result.risk_allowed is True


# ---------------------------------------------------------------------------
# TestDailyLossLimit
# ---------------------------------------------------------------------------

class TestDailyLossLimit:
    def test_daily_loss_at_limit_blocked(self):
        ctx = clear_ctx(daily_loss_limit=50.0, current_daily_loss=50.0)
        result = evaluate_risk(ctx)
        assert result.risk_allowed is False
        assert "daily_loss_limit_exceeded" in result.blocker_reasons

    def test_daily_loss_over_limit_blocked(self):
        ctx = clear_ctx(daily_loss_limit=50.0, current_daily_loss=60.0)
        result = evaluate_risk(ctx)
        assert "daily_loss_limit_exceeded" in result.blocker_reasons

    def test_daily_loss_below_limit_allowed(self):
        ctx = clear_ctx(daily_loss_limit=50.0, current_daily_loss=49.9)
        result = evaluate_risk(ctx)
        assert "daily_loss_limit_exceeded" not in result.blocker_reasons

    def test_daily_loss_zero_allowed(self):
        ctx = clear_ctx(daily_loss_limit=100.0, current_daily_loss=0.0)
        result = evaluate_risk(ctx)
        assert result.risk_allowed is True


# ---------------------------------------------------------------------------
# TestDailyTradeCap
# ---------------------------------------------------------------------------

class TestDailyTradeCap:
    def test_trade_count_at_cap_blocked(self):
        ctx = clear_ctx(daily_trade_cap=5, current_daily_trade_count=5)
        result = evaluate_risk(ctx)
        assert result.risk_allowed is False
        assert "daily_trade_cap_exceeded" in result.blocker_reasons

    def test_trade_count_over_cap_blocked(self):
        ctx = clear_ctx(daily_trade_cap=5, current_daily_trade_count=6)
        result = evaluate_risk(ctx)
        assert "daily_trade_cap_exceeded" in result.blocker_reasons

    def test_trade_count_below_cap_allowed(self):
        ctx = clear_ctx(daily_trade_cap=5, current_daily_trade_count=4)
        result = evaluate_risk(ctx)
        assert "daily_trade_cap_exceeded" not in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestEventLimit
# ---------------------------------------------------------------------------

class TestEventLimit:
    def test_event_positions_at_limit_blocked(self):
        ctx = clear_ctx(event_limit=2, current_event_open_positions=2)
        result = evaluate_risk(ctx)
        assert result.risk_allowed is False
        assert "event_limit_exceeded" in result.blocker_reasons

    def test_event_positions_over_limit_blocked(self):
        ctx = clear_ctx(event_limit=2, current_event_open_positions=3)
        result = evaluate_risk(ctx)
        assert "event_limit_exceeded" in result.blocker_reasons

    def test_event_positions_below_limit_allowed(self):
        ctx = clear_ctx(event_limit=2, current_event_open_positions=1)
        result = evaluate_risk(ctx)
        assert "event_limit_exceeded" not in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestMaxConcurrentPositions
# ---------------------------------------------------------------------------

class TestMaxConcurrentPositions:
    def test_concurrent_at_max_blocked(self):
        ctx = clear_ctx(max_concurrent_positions=3, current_open_positions=3)
        result = evaluate_risk(ctx)
        assert result.risk_allowed is False
        assert "max_concurrent_positions_exceeded" in result.blocker_reasons

    def test_concurrent_over_max_blocked(self):
        ctx = clear_ctx(max_concurrent_positions=3, current_open_positions=4)
        result = evaluate_risk(ctx)
        assert "max_concurrent_positions_exceeded" in result.blocker_reasons

    def test_concurrent_below_max_allowed(self):
        ctx = clear_ctx(max_concurrent_positions=3, current_open_positions=2)
        result = evaluate_risk(ctx)
        assert "max_concurrent_positions_exceeded" not in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestPositionSizeLimits
# ---------------------------------------------------------------------------

class TestPositionSizeLimits:
    def test_below_min_position_size_blocked(self):
        ctx = clear_ctx(min_position_size=5.0, requested_position_size=4.9)
        result = evaluate_risk(ctx)
        assert result.risk_allowed is False
        assert "below_min_position_size" in result.blocker_reasons

    def test_above_max_position_size_blocked(self):
        ctx = clear_ctx(max_position_size=100.0, requested_position_size=100.1)
        result = evaluate_risk(ctx)
        assert result.risk_allowed is False
        assert "above_max_position_size" in result.blocker_reasons

    def test_exact_min_position_size_allowed(self):
        ctx = clear_ctx(min_position_size=5.0, requested_position_size=5.0)
        result = evaluate_risk(ctx)
        assert "below_min_position_size" not in result.blocker_reasons

    def test_exact_max_position_size_allowed(self):
        ctx = clear_ctx(max_position_size=100.0, requested_position_size=100.0)
        result = evaluate_risk(ctx)
        assert "above_max_position_size" not in result.blocker_reasons

    def test_size_within_range_allowed(self):
        ctx = clear_ctx(min_position_size=5.0, max_position_size=100.0, requested_position_size=50.0)
        result = evaluate_risk(ctx)
        assert result.risk_allowed is True


# ---------------------------------------------------------------------------
# TestMultipleBlockers
# ---------------------------------------------------------------------------

class TestMultipleBlockers:
    def test_two_blockers_returned_together(self):
        ctx = clear_ctx(
            daily_loss_limit=50.0, current_daily_loss=50.0,
            daily_trade_cap=5, current_daily_trade_count=5,
        )
        result = evaluate_risk(ctx)
        assert result.risk_allowed is False
        assert "daily_loss_limit_exceeded" in result.blocker_reasons
        assert "daily_trade_cap_exceeded" in result.blocker_reasons
        assert len(result.blocker_reasons) == 2

    def test_all_blockers_returned_simultaneously(self):
        ctx = RiskContext(
            daily_loss_limit=10.0, current_daily_loss=10.0,
            daily_trade_cap=2, current_daily_trade_count=2,
            event_limit=1, current_event_open_positions=1,
            max_concurrent_positions=1, current_open_positions=1,
            min_position_size=5.0, max_position_size=5.0,
            requested_position_size=3.0,  # below min AND below max(=5) but not above
        )
        result = evaluate_risk(ctx)
        assert result.risk_allowed is False
        assert "daily_loss_limit_exceeded" in result.blocker_reasons
        assert "daily_trade_cap_exceeded" in result.blocker_reasons
        assert "event_limit_exceeded" in result.blocker_reasons
        assert "max_concurrent_positions_exceeded" in result.blocker_reasons
        assert "below_min_position_size" in result.blocker_reasons

    def test_blocker_count_matches_violations(self):
        ctx = clear_ctx(
            current_daily_loss=100.0, daily_loss_limit=100.0,  # triggers
            current_open_positions=5, max_concurrent_positions=5,  # triggers
        )
        result = evaluate_risk(ctx)
        assert len(result.blocker_reasons) == 2

    def test_all_checks_run_even_when_first_blocked(self):
        """All checks must run — first block must not short-circuit remaining checks."""
        ctx = clear_ctx(
            current_daily_loss=999.0, daily_loss_limit=10.0,  # blocks
            current_daily_trade_count=999, daily_trade_cap=5,  # also blocks
        )
        result = evaluate_risk(ctx)
        assert len(result.blocker_reasons) >= 2
        assert "daily_loss_limit_exceeded" in result.blocker_reasons
        assert "daily_trade_cap_exceeded" in result.blocker_reasons
