"""Tests for force sell evaluator — ForceSellContext, ForceSellDecision,
evaluate_force_sell()."""
from app.domain.force_sell.force_sell_context import ForceSellContext
from app.domain.force_sell.force_sell_decision import ForceSellDecision
from app.domain.force_sell.force_sell_evaluator import evaluate_force_sell


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ctx(
    time_remaining=60.0,
    force_sell_time_enabled=False,
    force_sell_time_seconds=10.0,
    force_sell_pnl_loss_enabled=False,
    force_sell_entry_delta_enabled=False,
    force_sell_entry_delta_threshold=0.10,
    force_sell_logic="any",
    entry_fill_price=0.50,
    current_price=0.50,
    current_pnl=0.0,
    side="YES",
):
    return ForceSellContext(
        time_remaining=time_remaining,
        force_sell_time_enabled=force_sell_time_enabled,
        force_sell_time_seconds=force_sell_time_seconds,
        force_sell_pnl_loss_enabled=force_sell_pnl_loss_enabled,
        force_sell_entry_delta_enabled=force_sell_entry_delta_enabled,
        force_sell_entry_delta_threshold=force_sell_entry_delta_threshold,
        force_sell_logic=force_sell_logic,
        entry_fill_price=entry_fill_price,
        current_price=current_price,
        current_pnl=current_pnl,
        side=side,
    )


# ---------------------------------------------------------------------------
# TestForceSellContext
# ---------------------------------------------------------------------------

class TestForceSellContext:
    def test_fields_are_set_correctly(self):
        ctx = ForceSellContext(
            time_remaining=5.0,
            force_sell_time_enabled=True,
            force_sell_time_seconds=10.0,
            force_sell_pnl_loss_enabled=True,
            force_sell_entry_delta_enabled=True,
            force_sell_entry_delta_threshold=0.15,
            force_sell_logic="all",
            entry_fill_price=0.60,
            current_price=0.40,
            current_pnl=-0.20,
            side="YES",
        )
        assert ctx.force_sell_logic == "all"
        assert ctx.side == "YES"
        assert ctx.entry_fill_price == 0.60
        assert ctx.force_sell_entry_delta_threshold == 0.15


# ---------------------------------------------------------------------------
# TestForceSellDecision
# ---------------------------------------------------------------------------

class TestForceSellDecision:
    def test_force_sell_true(self):
        d = ForceSellDecision(should_force_sell=True, reason="force_sell_time")
        assert d.should_force_sell is True
        assert d.reason == "force_sell_time"

    def test_force_sell_false(self):
        d = ForceSellDecision(should_force_sell=False)
        assert d.should_force_sell is False
        assert d.reason == ""


# ---------------------------------------------------------------------------
# TestNoConditionsEnabled
# ---------------------------------------------------------------------------

class TestNoConditionsEnabled:
    def test_no_conditions_enabled_returns_no_force_sell(self):
        ctx = _ctx(
            force_sell_time_enabled=False,
            force_sell_pnl_loss_enabled=False,
            force_sell_entry_delta_enabled=False,
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False
        assert result.reason == ""

    def test_result_is_never_none(self):
        ctx = _ctx()
        result = evaluate_force_sell(ctx)
        assert result is not None


# ---------------------------------------------------------------------------
# TestSingleCondition_Time
# ---------------------------------------------------------------------------

class TestSingleConditionTime:
    def test_time_triggers(self):
        """time_remaining <= time_seconds → force_sell_time."""
        ctx = _ctx(
            time_remaining=3.0,
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_time"

    def test_time_exact_threshold(self):
        """time_remaining == time_seconds triggers."""
        ctx = _ctx(
            time_remaining=5.0,
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_time"

    def test_time_above_threshold_no_trigger(self):
        """time_remaining > time_seconds → no trigger."""
        ctx = _ctx(
            time_remaining=20.0,
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False

    def test_time_disabled_no_trigger(self):
        """time condition disabled → no trigger even if below threshold."""
        ctx = _ctx(
            time_remaining=1.0,
            force_sell_time_enabled=False,
            force_sell_time_seconds=5.0,
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False


# ---------------------------------------------------------------------------
# TestSingleCondition_PnlLoss
# ---------------------------------------------------------------------------

class TestSingleConditionPnlLoss:
    def test_pnl_loss_triggers(self):
        """current_pnl < 0 with pnl_loss_enabled → force_sell_pnl_loss."""
        ctx = _ctx(
            force_sell_pnl_loss_enabled=True,
            current_pnl=-0.05,
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_pnl_loss"

    def test_pnl_zero_no_trigger(self):
        """current_pnl == 0 → no trigger (only negative triggers)."""
        ctx = _ctx(
            force_sell_pnl_loss_enabled=True,
            current_pnl=0.0,
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False

    def test_pnl_positive_no_trigger(self):
        """current_pnl > 0 → no trigger."""
        ctx = _ctx(
            force_sell_pnl_loss_enabled=True,
            current_pnl=0.10,
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False


# ---------------------------------------------------------------------------
# TestSingleCondition_EntryDelta
# ---------------------------------------------------------------------------

class TestSingleConditionEntryDelta:
    def test_entry_delta_yes_triggers(self):
        """YES position: price dropped past threshold → force_sell_entry_delta."""
        ctx = _ctx(
            force_sell_entry_delta_enabled=True,
            force_sell_entry_delta_threshold=0.10,
            entry_fill_price=0.60,
            current_price=0.45,  # adverse_move = 0.60-0.45 = 0.15 >= 0.10
            side="YES",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_entry_delta"

    def test_entry_delta_no_triggers(self):
        """NO position: price rose past threshold → force_sell_entry_delta."""
        ctx = _ctx(
            force_sell_entry_delta_enabled=True,
            force_sell_entry_delta_threshold=0.10,
            entry_fill_price=0.40,
            current_price=0.55,  # adverse_move = 0.55-0.40 = 0.15 >= 0.10
            side="NO",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_entry_delta"

    def test_entry_delta_below_threshold_no_trigger(self):
        """Adverse move below threshold → no trigger."""
        ctx = _ctx(
            force_sell_entry_delta_enabled=True,
            force_sell_entry_delta_threshold=0.20,
            entry_fill_price=0.60,
            current_price=0.55,  # adverse_move = 0.05 < 0.20
            side="YES",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False

    def test_entry_delta_yes_no_loss_no_trigger(self):
        """YES position with price above entry → no adverse move."""
        ctx = _ctx(
            force_sell_entry_delta_enabled=True,
            force_sell_entry_delta_threshold=0.10,
            entry_fill_price=0.40,
            current_price=0.60,  # price went UP (profit for YES) → no adverse move
            side="YES",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False


# ---------------------------------------------------------------------------
# TestCombinator_Any
# ---------------------------------------------------------------------------

class TestCombinatorAny:
    def test_any_both_enabled_only_time_fires(self):
        """any + time+pnl enabled, only time fires → force_sell_combined_any."""
        ctx = _ctx(
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
            time_remaining=3.0,
            force_sell_pnl_loss_enabled=True,
            current_pnl=0.10,  # pnl positive → no pnl trigger
            force_sell_logic="any",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_combined_any"

    def test_any_both_enabled_both_fire(self):
        """any + time+pnl enabled, both fire → force_sell_combined_any."""
        ctx = _ctx(
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
            time_remaining=3.0,
            force_sell_pnl_loss_enabled=True,
            current_pnl=-0.10,
            force_sell_logic="any",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_combined_any"

    def test_any_both_enabled_neither_fires(self):
        """any + time+pnl enabled, neither fires → no force sell."""
        ctx = _ctx(
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
            time_remaining=100.0,
            force_sell_pnl_loss_enabled=True,
            current_pnl=0.10,
            force_sell_logic="any",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False


# ---------------------------------------------------------------------------
# TestCombinator_All
# ---------------------------------------------------------------------------

class TestCombinatorAll:
    def test_all_both_enabled_only_time_fires(self):
        """all + time+pnl enabled, only time fires → no force sell."""
        ctx = _ctx(
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
            time_remaining=3.0,
            force_sell_pnl_loss_enabled=True,
            current_pnl=0.10,  # pnl positive
            force_sell_logic="all",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False

    def test_all_both_enabled_both_fire(self):
        """all + time+pnl enabled, both fire → force_sell_combined_all."""
        ctx = _ctx(
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
            time_remaining=3.0,
            force_sell_pnl_loss_enabled=True,
            current_pnl=-0.10,
            force_sell_logic="all",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_combined_all"

    def test_all_three_enabled_all_fire(self):
        """all + 3 conditions enabled, all fire → force_sell_combined_all."""
        ctx = _ctx(
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
            time_remaining=3.0,
            force_sell_pnl_loss_enabled=True,
            current_pnl=-0.10,
            force_sell_entry_delta_enabled=True,
            force_sell_entry_delta_threshold=0.10,
            entry_fill_price=0.60,
            current_price=0.45,
            force_sell_logic="all",
            side="YES",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is True
        assert result.reason == "force_sell_combined_all"

    def test_all_three_enabled_two_fire(self):
        """all + 3 conditions enabled, only 2 fire → no force sell."""
        ctx = _ctx(
            force_sell_time_enabled=True,
            force_sell_time_seconds=5.0,
            time_remaining=3.0,
            force_sell_pnl_loss_enabled=True,
            current_pnl=-0.10,
            force_sell_entry_delta_enabled=True,
            force_sell_entry_delta_threshold=0.20,
            entry_fill_price=0.60,
            current_price=0.55,  # adverse = 0.05 < 0.20 → delta does not fire
            force_sell_logic="all",
            side="YES",
        )
        result = evaluate_force_sell(ctx)
        assert result.should_force_sell is False


# ---------------------------------------------------------------------------
# TestReasonCodes
# ---------------------------------------------------------------------------

class TestReasonCodes:
    def test_reason_code_force_sell_time(self):
        ctx = _ctx(force_sell_time_enabled=True, time_remaining=1.0,
                   force_sell_time_seconds=5.0)
        assert evaluate_force_sell(ctx).reason == "force_sell_time"

    def test_reason_code_force_sell_pnl_loss(self):
        ctx = _ctx(force_sell_pnl_loss_enabled=True, current_pnl=-0.01)
        assert evaluate_force_sell(ctx).reason == "force_sell_pnl_loss"

    def test_reason_code_force_sell_entry_delta(self):
        ctx = _ctx(force_sell_entry_delta_enabled=True,
                   force_sell_entry_delta_threshold=0.10,
                   entry_fill_price=0.60, current_price=0.45, side="YES")
        assert evaluate_force_sell(ctx).reason == "force_sell_entry_delta"

    def test_reason_code_empty_when_no_trigger(self):
        ctx = _ctx()  # all disabled
        assert evaluate_force_sell(ctx).reason == ""
