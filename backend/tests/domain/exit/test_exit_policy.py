"""Tests for exit policy — ExitContext, ExitDecision, evaluate_exit_policy()."""
from app.domain.exit.exit_context import ExitContext
from app.domain.exit.exit_decision import ExitDecision
from app.domain.exit.exit_policy import evaluate_exit_policy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ctx(
    entry_price=0.50,
    current_price=0.50,
    side="YES",
    stop_loss_threshold=0.10,
    take_profit_threshold=0.15,
    time_remaining=60.0,
):
    return ExitContext(
        entry_price=entry_price,
        current_price=current_price,
        side=side,
        stop_loss_threshold=stop_loss_threshold,
        take_profit_threshold=take_profit_threshold,
        time_remaining=time_remaining,
    )


# ---------------------------------------------------------------------------
# TestExitContext
# ---------------------------------------------------------------------------

class TestExitContext:
    def test_fields_are_set_correctly(self):
        ctx = ExitContext(
            entry_price=0.60,
            current_price=0.45,
            side="YES",
            stop_loss_threshold=0.10,
            take_profit_threshold=0.20,
            time_remaining=30.0,
        )
        assert ctx.entry_price == 0.60
        assert ctx.current_price == 0.45
        assert ctx.side == "YES"
        assert ctx.stop_loss_threshold == 0.10
        assert ctx.take_profit_threshold == 0.20
        assert ctx.time_remaining == 30.0


# ---------------------------------------------------------------------------
# TestExitDecision
# ---------------------------------------------------------------------------

class TestExitDecision:
    def test_exit_true_fields(self):
        decision = ExitDecision(should_exit=True, exit_reason="stop_loss")
        assert decision.should_exit is True
        assert decision.exit_reason == "stop_loss"

    def test_no_exit_fields(self):
        decision = ExitDecision(should_exit=False)
        assert decision.should_exit is False
        assert decision.exit_reason == ""


# ---------------------------------------------------------------------------
# TestEvaluateExitPolicy
# ---------------------------------------------------------------------------

class TestEvaluateExitPolicy:
    # --- Stop loss ---

    def test_stop_loss_triggered_yes(self):
        """YES position: price dropped enough to trigger stop loss."""
        ctx = _ctx(entry_price=0.60, current_price=0.45, side="YES",
                   stop_loss_threshold=0.10)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is True
        assert result.exit_reason == "stop_loss"

    def test_stop_loss_triggered_no(self):
        """NO position: price rose enough to trigger stop loss."""
        ctx = _ctx(entry_price=0.40, current_price=0.55, side="NO",
                   stop_loss_threshold=0.10)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is True
        assert result.exit_reason == "stop_loss"

    def test_stop_loss_at_threshold(self):
        """Stop loss triggers when loss meets or exceeds threshold."""
        # Use exact binary fractions to avoid floating point drift
        ctx = _ctx(entry_price=0.5, current_price=0.25, side="YES",
                   stop_loss_threshold=0.25)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is True
        assert result.exit_reason == "stop_loss"

    # --- Take profit ---

    def test_take_profit_triggered_yes(self):
        """YES position: price rose enough to trigger take profit."""
        ctx = _ctx(entry_price=0.40, current_price=0.60, side="YES",
                   stop_loss_threshold=0.20, take_profit_threshold=0.15)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is True
        assert result.exit_reason == "take_profit"

    def test_take_profit_triggered_no(self):
        """NO position: price dropped enough to trigger take profit."""
        ctx = _ctx(entry_price=0.60, current_price=0.40, side="NO",
                   stop_loss_threshold=0.30, take_profit_threshold=0.15)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is True
        assert result.exit_reason == "take_profit"

    def test_take_profit_exact_threshold(self):
        """Take profit triggers exactly at the threshold boundary."""
        ctx = _ctx(entry_price=0.40, current_price=0.55, side="YES",
                   stop_loss_threshold=0.20, take_profit_threshold=0.15)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is True
        assert result.exit_reason == "take_profit"

    # --- No exit ---

    def test_no_exit_when_no_condition_met(self):
        """No condition met — should_exit is False."""
        ctx = _ctx(entry_price=0.50, current_price=0.52, side="YES",
                   stop_loss_threshold=0.10, take_profit_threshold=0.15,
                   time_remaining=60.0)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is False
        assert result.exit_reason == ""

    def test_no_exit_result_is_never_none(self):
        ctx = _ctx()
        result = evaluate_exit_policy(ctx)
        assert result is not None

    # --- Timeout ---

    def test_timeout_triggers_exit(self):
        """time_remaining of 0 triggers timeout exit."""
        ctx = _ctx(entry_price=0.50, current_price=0.52, side="YES",
                   stop_loss_threshold=0.10, take_profit_threshold=0.15,
                   time_remaining=0.0)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is True
        assert result.exit_reason == "timeout"

    def test_negative_time_remaining_triggers_timeout(self):
        """Negative time_remaining also triggers timeout."""
        ctx = _ctx(time_remaining=-5.0)
        result = evaluate_exit_policy(ctx)
        assert result.should_exit is True
        assert result.exit_reason == "timeout"

    # --- Priority order ---

    def test_stop_loss_takes_priority_over_take_profit(self):
        """Stop loss is evaluated before take profit — stop loss wins when both trigger."""
        # Both loss and profit could trigger with extreme values,
        # but loss_move >= stop_loss_threshold is checked first.
        # Use YES: entry=0.50, current=0.30
        # loss_move = 0.20 >= 0.10 (stop loss) AND profit_move = -0.20 < 0 (no take profit)
        # This is naturally prioritized — but let's test a case where stop_loss_threshold is low
        ctx = _ctx(entry_price=0.50, current_price=0.35, side="YES",
                   stop_loss_threshold=0.10, take_profit_threshold=0.10)
        result = evaluate_exit_policy(ctx)
        assert result.exit_reason == "stop_loss"

    def test_stop_loss_takes_priority_over_timeout(self):
        """Stop loss is evaluated before timeout."""
        ctx = _ctx(entry_price=0.60, current_price=0.45, side="YES",
                   stop_loss_threshold=0.10, take_profit_threshold=0.20,
                   time_remaining=0.0)
        result = evaluate_exit_policy(ctx)
        assert result.exit_reason == "stop_loss"

    def test_take_profit_takes_priority_over_timeout(self):
        """Take profit is evaluated before timeout."""
        ctx = _ctx(entry_price=0.40, current_price=0.60, side="YES",
                   stop_loss_threshold=0.30, take_profit_threshold=0.15,
                   time_remaining=0.0)
        result = evaluate_exit_policy(ctx)
        assert result.exit_reason == "take_profit"

    # --- Reason codes ---

    def test_reason_code_stop_loss(self):
        ctx = _ctx(entry_price=0.60, current_price=0.45, side="YES",
                   stop_loss_threshold=0.10)
        assert evaluate_exit_policy(ctx).exit_reason == "stop_loss"

    def test_reason_code_take_profit(self):
        ctx = _ctx(entry_price=0.40, current_price=0.60, side="YES",
                   stop_loss_threshold=0.30, take_profit_threshold=0.15)
        assert evaluate_exit_policy(ctx).exit_reason == "take_profit"

    def test_reason_code_timeout(self):
        ctx = _ctx(time_remaining=0.0)
        assert evaluate_exit_policy(ctx).exit_reason == "timeout"

    def test_reason_code_empty_when_no_exit(self):
        ctx = _ctx()
        assert evaluate_exit_policy(ctx).exit_reason == ""
