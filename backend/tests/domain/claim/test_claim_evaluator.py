"""Tests for claim/settlement state evaluation — v0.5.6."""
from app.domain.claim.claim_status import ClaimStatus
from app.domain.claim.claim_context import ClaimContext
from app.domain.claim.claim_result import ClaimResult
from app.domain.claim.claim_evaluator import evaluate_claim_state


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def base_ctx(**overrides) -> ClaimContext:
    """Base context with all gates open and no lifecycle flags set."""
    defaults = dict(
        event_outcome_known=True,
        resolution_finalized=True,
        claim_available=True,
        claim_submitted=False,
        claim_completed=False,
        claim_failed=False,
        claimed_amount=0.0,
        settlement_completed_at=None,
        balance_before_claim=1000.0,
        early_exit_realized_pnl=0.0,
        settlement_effect=0.0,
        claim_adjusted_balance_effect=0.0,
    )
    defaults.update(overrides)
    return ClaimContext(**defaults)


# ---------------------------------------------------------------------------
# TestClaimStatus
# ---------------------------------------------------------------------------

class TestClaimStatus:
    def test_all_status_values_present(self):
        expected = {
            "not_claimable_outcome_unknown",
            "not_claimable_resolution_pending",
            "not_claimable_claim_unavailable",
            "claim_available",
            "claim_submitted",
            "claim_completed",
            "claim_failed",
        }
        actual = {s.value for s in ClaimStatus}
        assert expected == actual

    def test_from_string(self):
        assert ClaimStatus("claim_completed") == ClaimStatus.CLAIM_COMPLETED

    def test_not_claimable_statuses_are_distinct(self):
        assert ClaimStatus.NOT_CLAIMABLE_OUTCOME_UNKNOWN != ClaimStatus.NOT_CLAIMABLE_RESOLUTION_PENDING
        assert ClaimStatus.NOT_CLAIMABLE_RESOLUTION_PENDING != ClaimStatus.NOT_CLAIMABLE_CLAIM_UNAVAILABLE


# ---------------------------------------------------------------------------
# TestClaimResult
# ---------------------------------------------------------------------------

class TestClaimResult:
    def test_claim_result_fields(self):
        result = ClaimResult(
            claim_status=ClaimStatus.CLAIM_AVAILABLE,
            is_claimable=True,
            balance_after_claim=1000.0,
            claimed_amount=0.0,
            claim_adjusted_balance_effect=0.0,
            early_exit_realized_pnl=5.0,
            settlement_effect=0.0,
            settlement_completed_at=None,
        )
        assert result.claim_status == ClaimStatus.CLAIM_AVAILABLE
        assert result.is_claimable is True
        assert result.early_exit_realized_pnl == 5.0


# ---------------------------------------------------------------------------
# TestGateChecks — not claimable paths
# ---------------------------------------------------------------------------

class TestGateChecks:
    def test_outcome_unknown_produces_not_claimable(self):
        ctx = base_ctx(event_outcome_known=False, resolution_finalized=False, claim_available=False)
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.NOT_CLAIMABLE_OUTCOME_UNKNOWN
        assert result.is_claimable is False

    def test_outcome_unknown_checked_before_resolution(self):
        """outcome_unknown gate fires even if resolution_finalized=True."""
        ctx = base_ctx(event_outcome_known=False, resolution_finalized=True, claim_available=True)
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.NOT_CLAIMABLE_OUTCOME_UNKNOWN

    def test_resolution_pending_produces_not_claimable(self):
        ctx = base_ctx(resolution_finalized=False, claim_available=False)
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.NOT_CLAIMABLE_RESOLUTION_PENDING
        assert result.is_claimable is False

    def test_resolution_pending_checked_before_claim_available(self):
        ctx = base_ctx(resolution_finalized=False, claim_available=True)
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.NOT_CLAIMABLE_RESOLUTION_PENDING

    def test_claim_unavailable_produces_not_claimable(self):
        ctx = base_ctx(claim_available=False)
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.NOT_CLAIMABLE_CLAIM_UNAVAILABLE
        assert result.is_claimable is False

    def test_not_claimable_balance_unchanged(self):
        ctx = base_ctx(event_outcome_known=False, balance_before_claim=500.0)
        result = evaluate_claim_state(ctx)
        assert result.balance_after_claim == 500.0


# ---------------------------------------------------------------------------
# TestClaimAvailable
# ---------------------------------------------------------------------------

class TestClaimAvailable:
    def test_all_gates_open_produces_claim_available(self):
        ctx = base_ctx()
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.CLAIM_AVAILABLE
        assert result.is_claimable is True

    def test_claim_available_balance_unchanged(self):
        ctx = base_ctx(balance_before_claim=750.0)
        result = evaluate_claim_state(ctx)
        assert result.balance_after_claim == 750.0

    def test_claim_available_is_claimable_true(self):
        ctx = base_ctx()
        result = evaluate_claim_state(ctx)
        assert result.is_claimable is True


# ---------------------------------------------------------------------------
# TestClaimLifecycle
# ---------------------------------------------------------------------------

class TestClaimLifecycle:
    def test_claim_submitted_status(self):
        ctx = base_ctx(claim_submitted=True)
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.CLAIM_SUBMITTED
        assert result.is_claimable is False

    def test_claim_submitted_balance_unchanged(self):
        ctx = base_ctx(claim_submitted=True, balance_before_claim=800.0)
        result = evaluate_claim_state(ctx)
        assert result.balance_after_claim == 800.0

    def test_claim_completed_status(self):
        ctx = base_ctx(claim_completed=True, claimed_amount=100.0, balance_before_claim=500.0)
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.CLAIM_COMPLETED
        assert result.is_claimable is False

    def test_claim_completed_updates_balance(self):
        ctx = base_ctx(
            claim_completed=True,
            claimed_amount=100.0,
            balance_before_claim=500.0,
            claim_adjusted_balance_effect=0.0,
        )
        result = evaluate_claim_state(ctx)
        assert result.balance_after_claim == 600.0

    def test_claim_completed_includes_adjusted_effect(self):
        ctx = base_ctx(
            claim_completed=True,
            claimed_amount=100.0,
            balance_before_claim=500.0,
            claim_adjusted_balance_effect=10.0,
        )
        result = evaluate_claim_state(ctx)
        assert result.balance_after_claim == 610.0

    def test_claim_failed_status(self):
        ctx = base_ctx(claim_failed=True)
        result = evaluate_claim_state(ctx)
        assert result.claim_status == ClaimStatus.CLAIM_FAILED
        assert result.is_claimable is False

    def test_claim_failed_balance_unchanged(self):
        ctx = base_ctx(claim_failed=True, balance_before_claim=300.0)
        result = evaluate_claim_state(ctx)
        assert result.balance_after_claim == 300.0


# ---------------------------------------------------------------------------
# TestPnLSeparation
# ---------------------------------------------------------------------------

class TestPnLSeparation:
    def test_early_exit_pnl_carried_separately(self):
        ctx = base_ctx(
            claim_completed=True,
            claimed_amount=50.0,
            balance_before_claim=200.0,
            early_exit_realized_pnl=15.0,
            settlement_effect=0.0,
        )
        result = evaluate_claim_state(ctx)
        assert result.early_exit_realized_pnl == 15.0
        # early exit pnl is NOT added to balance_after_claim
        assert result.balance_after_claim == 250.0

    def test_settlement_effect_carried_separately(self):
        ctx = base_ctx(
            claim_completed=True,
            claimed_amount=50.0,
            balance_before_claim=200.0,
            early_exit_realized_pnl=0.0,
            settlement_effect=25.0,
        )
        result = evaluate_claim_state(ctx)
        assert result.settlement_effect == 25.0
        # settlement_effect is separate from balance_after_claim computation
        assert result.balance_after_claim == 250.0

    def test_early_exit_and_settlement_are_distinct_fields(self):
        ctx = base_ctx(early_exit_realized_pnl=10.0, settlement_effect=20.0)
        result = evaluate_claim_state(ctx)
        assert result.early_exit_realized_pnl == 10.0
        assert result.settlement_effect == 20.0
        assert result.early_exit_realized_pnl != result.settlement_effect

    def test_early_exit_pnl_carried_in_blocked_state(self):
        ctx = base_ctx(event_outcome_known=False, early_exit_realized_pnl=8.0)
        result = evaluate_claim_state(ctx)
        assert result.early_exit_realized_pnl == 8.0

    def test_settlement_effect_carried_in_blocked_state(self):
        ctx = base_ctx(resolution_finalized=False, settlement_effect=12.0)
        result = evaluate_claim_state(ctx)
        assert result.settlement_effect == 12.0


# ---------------------------------------------------------------------------
# TestRelayerSeam
# ---------------------------------------------------------------------------

class TestRelayerSeam:
    def test_claim_adjusted_balance_effect_carried_in_result(self):
        ctx = base_ctx(claim_adjusted_balance_effect=5.0)
        result = evaluate_claim_state(ctx)
        assert result.claim_adjusted_balance_effect == 5.0

    def test_claim_adjusted_balance_effect_zero_default(self):
        ctx = base_ctx()
        result = evaluate_claim_state(ctx)
        assert result.claim_adjusted_balance_effect == 0.0

    def test_settlement_completed_at_carried(self):
        ctx = base_ctx(
            claim_completed=True,
            claimed_amount=100.0,
            balance_before_claim=500.0,
            settlement_completed_at="2026-04-02T12:00:00Z",
        )
        result = evaluate_claim_state(ctx)
        assert result.settlement_completed_at == "2026-04-02T12:00:00Z"

    def test_settlement_completed_at_none_when_not_completed(self):
        ctx = base_ctx()
        result = evaluate_claim_state(ctx)
        assert result.settlement_completed_at is None

    def test_claimed_amount_carried_in_result(self):
        ctx = base_ctx(
            claim_completed=True,
            claimed_amount=77.5,
            balance_before_claim=500.0,
        )
        result = evaluate_claim_state(ctx)
        assert result.claimed_amount == 77.5
