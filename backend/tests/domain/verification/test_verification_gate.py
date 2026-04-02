"""Tests for verification gate — VerificationContext, VerificationResult, evaluate_verification."""
from app.domain.verification.verification_context import VerificationContext
from app.domain.verification.verification_gate import evaluate_verification
from app.domain.verification.verification_result import VerificationResult


class TestVerificationContext:
    def test_defaults_are_all_invalid(self):
        ctx = VerificationContext()
        assert ctx.ref_valid is False
        assert ctx.market_valid is False
        assert ctx.settings_ok is False

    def test_fully_valid_context(self):
        ctx = VerificationContext(ref_valid=True, market_valid=True, settings_ok=True)
        assert ctx.ref_valid is True
        assert ctx.market_valid is True
        assert ctx.settings_ok is True


class TestVerificationResult:
    def test_trade_allowed_fields(self):
        result = VerificationResult(trade_allowed=True)
        assert result.trade_allowed is True
        assert result.blocker_reasons == []

    def test_trade_blocked_with_reasons(self):
        result = VerificationResult(
            trade_allowed=False,
            blocker_reasons=["ref_invalid", "market_invalid"],
        )
        assert result.trade_allowed is False
        assert len(result.blocker_reasons) == 2


class TestEvaluateVerification:
    def test_ref_invalid_blocks_trade(self):
        ctx = VerificationContext(ref_valid=False, market_valid=True, settings_ok=True)
        result = evaluate_verification(ctx)
        assert result.trade_allowed is False
        assert "ref_invalid" in result.blocker_reasons

    def test_market_invalid_blocks_trade(self):
        ctx = VerificationContext(ref_valid=True, market_valid=False, settings_ok=True)
        result = evaluate_verification(ctx)
        assert result.trade_allowed is False
        assert "market_invalid" in result.blocker_reasons

    def test_settings_not_ok_blocks_trade(self):
        ctx = VerificationContext(ref_valid=True, market_valid=True, settings_ok=False)
        result = evaluate_verification(ctx)
        assert result.trade_allowed is False
        assert "settings_not_ok" in result.blocker_reasons

    def test_all_valid_allows_trade(self):
        ctx = VerificationContext(ref_valid=True, market_valid=True, settings_ok=True)
        result = evaluate_verification(ctx)
        assert result.trade_allowed is True
        assert result.blocker_reasons == []

    def test_multiple_blockers_all_in_reason_list(self):
        ctx = VerificationContext(ref_valid=False, market_valid=False, settings_ok=False)
        result = evaluate_verification(ctx)
        assert result.trade_allowed is False
        assert "ref_invalid" in result.blocker_reasons
        assert "market_invalid" in result.blocker_reasons
        assert "settings_not_ok" in result.blocker_reasons
        assert len(result.blocker_reasons) == 3

    def test_fail_closed_single_blocker_denies_trade(self):
        """Any single blocker is sufficient to deny trade — fail-closed."""
        ctx = VerificationContext(ref_valid=True, market_valid=True, settings_ok=False)
        result = evaluate_verification(ctx)
        assert result.trade_allowed is False

    def test_default_context_blocks_all(self):
        """Default VerificationContext (all False) must block trade."""
        result = evaluate_verification(VerificationContext())
        assert result.trade_allowed is False
        assert "ref_invalid" in result.blocker_reasons
        assert "market_invalid" in result.blocker_reasons
        assert "settings_not_ok" in result.blocker_reasons

    def test_strategy_eligible_but_verification_fails_blocks_trade(self):
        """Verification is independent of strategy — failure always hard-blocks."""
        # Even if strategy would say eligible, verification failure blocks
        ctx = VerificationContext(ref_valid=False, market_valid=True, settings_ok=True)
        result = evaluate_verification(ctx)
        assert result.trade_allowed is False
        assert "ref_invalid" in result.blocker_reasons

    def test_all_valid_produces_no_blockers(self):
        ctx = VerificationContext(ref_valid=True, market_valid=True, settings_ok=True)
        result = evaluate_verification(ctx)
        assert len(result.blocker_reasons) == 0
