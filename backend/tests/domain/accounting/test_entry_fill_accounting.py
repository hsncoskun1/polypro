"""Tests for entry_fill_accounting — compute_entry_fill_accounting()."""
import pytest
from app.domain.accounting.accounting_context import AccountingContext
from app.domain.accounting.entry_fill_accounting import compute_entry_fill_accounting


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ctx(
    side="YES",
    entry_trigger_price=0.48,
    entry_order_submitted_price=0.49,
    entry_fill_price=0.50,
    current_price=0.55,
    requested_size=10.0,
    filled_size=10.0,
    total_balance=1000.0,
    available_balance=900.0,
    session_start_balance=1000.0,
    prior_session_realized_pnl=0.0,
    claim_adjusted_balance_effect=0.0,
):
    return AccountingContext(
        side=side,
        entry_trigger_price=entry_trigger_price,
        entry_order_submitted_price=entry_order_submitted_price,
        entry_fill_price=entry_fill_price,
        current_price=current_price,
        requested_size=requested_size,
        filled_size=filled_size,
        total_balance=total_balance,
        available_balance=available_balance,
        session_start_balance=session_start_balance,
        prior_session_realized_pnl=prior_session_realized_pnl,
        claim_adjusted_balance_effect=claim_adjusted_balance_effect,
    )


# ---------------------------------------------------------------------------
# TestEntryFillAccountingSnapshot
# ---------------------------------------------------------------------------

class TestEntryFillAccountingSnapshot:
    def test_entry_fill_accounting_snapshot_correct(self):
        """Entry fill accounting produces correct snapshot for YES position."""
        ctx = _ctx(
            side="YES",
            entry_trigger_price=0.48,
            entry_order_submitted_price=0.49,
            entry_fill_price=0.50,
            current_price=0.55,
            filled_size=10.0,
            session_start_balance=1000.0,
        )
        snap = compute_entry_fill_accounting(ctx)
        assert snap.side == "YES"
        assert snap.entry_fill_price == 0.50
        assert snap.entry_order_submitted_price == 0.49
        assert snap.entry_trigger_price == 0.48
        assert snap.current_price == 0.55

    def test_unrealized_pnl_computed_correctly(self):
        """Unrealized PnL = (current - entry_fill) * size for YES."""
        ctx = _ctx(entry_fill_price=0.50, current_price=0.60, filled_size=10.0)
        snap = compute_entry_fill_accounting(ctx)
        assert snap.unrealized_pnl == pytest.approx(1.0)

    def test_realized_pnl_is_zero_at_entry(self):
        """Position just opened — realized PnL must be 0.0."""
        snap = compute_entry_fill_accounting(_ctx())
        assert snap.realized_pnl == pytest.approx(0.0)

    def test_exit_prices_are_zero_at_entry(self):
        """Exit price fields are 0.0 — position not yet closed."""
        snap = compute_entry_fill_accounting(_ctx())
        assert snap.exit_fill_price == 0.0
        assert snap.exit_trigger_price == 0.0
        assert snap.exit_order_submitted_price == 0.0

    def test_trigger_submitted_fill_separation_maintained(self):
        """All three entry price moments are distinct and stored separately."""
        ctx = _ctx(
            entry_trigger_price=0.48,
            entry_order_submitted_price=0.49,
            entry_fill_price=0.50,
        )
        snap = compute_entry_fill_accounting(ctx)
        assert snap.entry_trigger_price == 0.48
        assert snap.entry_order_submitted_price == 0.49
        assert snap.entry_fill_price == 0.50
        assert snap.entry_trigger_price != snap.entry_order_submitted_price
        assert snap.entry_order_submitted_price != snap.entry_fill_price

    def test_order_submitted_price_not_used_for_pnl(self):
        """PnL is based on fill price, not submitted price."""
        # entry_fill=0.50, submitted=0.55, current=0.60
        # PnL should be (0.60-0.50)*10=1.0, NOT (0.60-0.55)*10=0.5
        ctx = _ctx(
            entry_order_submitted_price=0.55,
            entry_fill_price=0.50,
            current_price=0.60,
            filled_size=10.0,
        )
        snap = compute_entry_fill_accounting(ctx)
        assert snap.unrealized_pnl == pytest.approx(1.0)

    def test_session_balance_fields(self):
        """Session balance fields computed correctly at entry."""
        ctx = _ctx(session_start_balance=1000.0, prior_session_realized_pnl=0.0)
        snap = compute_entry_fill_accounting(ctx)
        assert snap.session_start_balance == 1000.0
        assert snap.session_realized_pnl == pytest.approx(0.0)
        assert snap.current_balance == pytest.approx(1000.0)

    def test_total_balance_and_available_balance_carried(self):
        """total_balance and available_balance carried through from context."""
        ctx = _ctx(total_balance=5000.0, available_balance=4000.0)
        snap = compute_entry_fill_accounting(ctx)
        assert snap.total_balance == 5000.0
        assert snap.available_balance == 4000.0

    def test_entry_trigger_move_value(self):
        """entry_trigger_move_value = fill - trigger (YES side)."""
        ctx = _ctx(entry_trigger_price=0.48, entry_fill_price=0.50, side="YES")
        snap = compute_entry_fill_accounting(ctx)
        assert snap.entry_trigger_move_value == pytest.approx(0.02)

    def test_no_side_unrealized_pnl(self):
        """NO position: price fell from fill → positive unrealized PnL."""
        ctx = _ctx(
            side="NO",
            entry_fill_price=0.60,
            current_price=0.50,
            filled_size=10.0,
        )
        snap = compute_entry_fill_accounting(ctx)
        assert snap.unrealized_pnl == pytest.approx(1.0)

    def test_session_with_prior_realized_pnl(self):
        """Prior session realized PnL accumulates into session_realized_pnl."""
        ctx = _ctx(
            session_start_balance=1000.0,
            prior_session_realized_pnl=5.0,
        )
        snap = compute_entry_fill_accounting(ctx)
        assert snap.session_realized_pnl == pytest.approx(5.0)
        assert snap.current_balance == pytest.approx(1005.0)
