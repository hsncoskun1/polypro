"""Tests for live execution preflight + outbound guard — v0.7.2."""
from app.domain.live.outbound_action_type import OutboundActionType
from app.domain.live.preflight_context import PreflightContext
from app.domain.live.preflight_result import PreflightResult
from app.domain.live.preflight_evaluator import evaluate_preflight


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def simulation_ctx(**overrides) -> PreflightContext:
    """Simulation default — live not requested, all gates failed."""
    defaults = dict(
        simulation_mode_default=True,
        live_mode_requested=False,
        live_mode_enabled=False,
        explicit_live_enable=False,
        credentials_complete=False,
        verification_passed=False,
        sizing_passed=False,
        risk_passed=False,
        outbound_action_type=OutboundActionType.LIVE_ORDER_SUBMIT,
    )
    defaults.update(overrides)
    return PreflightContext(**defaults)


def all_clear_ctx(**overrides) -> PreflightContext:
    """All preflight conditions met — live outbound allowed."""
    defaults = dict(
        simulation_mode_default=False,
        live_mode_requested=True,
        live_mode_enabled=True,
        explicit_live_enable=True,
        credentials_complete=True,
        verification_passed=True,
        sizing_passed=True,
        risk_passed=True,
        outbound_action_type=OutboundActionType.LIVE_ORDER_SUBMIT,
    )
    defaults.update(overrides)
    return PreflightContext(**defaults)


# ---------------------------------------------------------------------------
# TestOutboundActionType
# ---------------------------------------------------------------------------

class TestOutboundActionType:
    def test_live_order_submit_value(self):
        assert OutboundActionType.LIVE_ORDER_SUBMIT == "live_order_submit"

    def test_live_order_cancel_value(self):
        assert OutboundActionType.LIVE_ORDER_CANCEL == "live_order_cancel"

    def test_live_claim_submit_value(self):
        assert OutboundActionType.LIVE_CLAIM_SUBMIT == "live_claim_submit"

    def test_other_live_outbound_value(self):
        assert OutboundActionType.OTHER_LIVE_OUTBOUND == "other_live_outbound"

    def test_is_str_enum(self):
        assert isinstance(OutboundActionType.LIVE_ORDER_SUBMIT, str)


# ---------------------------------------------------------------------------
# TestPreflightResult
# ---------------------------------------------------------------------------

class TestPreflightResult:
    def test_allowed_result(self):
        result = PreflightResult(outbound_allowed=True, blocker_reasons=[])
        assert result.outbound_allowed is True
        assert result.blocker_reasons == []

    def test_blocked_result(self):
        result = PreflightResult(outbound_allowed=False, blocker_reasons=["risk_not_passed"])
        assert result.outbound_allowed is False
        assert "risk_not_passed" in result.blocker_reasons

    def test_blocker_reasons_default_empty(self):
        result = PreflightResult(outbound_allowed=True)
        assert result.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestSimulationGate
# ---------------------------------------------------------------------------

class TestSimulationGate:
    def test_simulation_default_blocks_live_outbound(self):
        result = evaluate_preflight(simulation_ctx())
        assert result.outbound_allowed is False
        assert "outbound_not_allowed_in_simulation" in result.blocker_reasons

    def test_simulation_default_single_blocker_reason(self):
        """Simulation gate produces exactly one blocker — clean, not noisy."""
        result = evaluate_preflight(simulation_ctx())
        assert result.blocker_reasons == ["outbound_not_allowed_in_simulation"]

    def test_simulation_gate_stops_further_checks(self):
        """Simulation gate must not produce additional live-path blockers."""
        result = evaluate_preflight(simulation_ctx())
        assert "explicit_live_enable_required" not in result.blocker_reasons
        assert "live_credentials_incomplete" not in result.blocker_reasons
        assert "risk_not_passed" not in result.blocker_reasons

    def test_simulation_gate_applies_regardless_of_action_type(self):
        for action in OutboundActionType:
            ctx = simulation_ctx(outbound_action_type=action)
            result = evaluate_preflight(ctx)
            assert result.outbound_allowed is False
            assert "outbound_not_allowed_in_simulation" in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestAllClear
# ---------------------------------------------------------------------------

class TestAllClear:
    def test_all_clear_outbound_allowed(self):
        result = evaluate_preflight(all_clear_ctx())
        assert result.outbound_allowed is True
        assert result.blocker_reasons == []

    def test_all_clear_with_order_cancel(self):
        result = evaluate_preflight(all_clear_ctx(outbound_action_type=OutboundActionType.LIVE_ORDER_CANCEL))
        assert result.outbound_allowed is True

    def test_all_clear_with_claim_submit(self):
        result = evaluate_preflight(all_clear_ctx(outbound_action_type=OutboundActionType.LIVE_CLAIM_SUBMIT))
        assert result.outbound_allowed is True


# ---------------------------------------------------------------------------
# TestIndividualBlockers
# ---------------------------------------------------------------------------

class TestIndividualBlockers:
    def test_explicit_live_enable_missing_blocked(self):
        ctx = all_clear_ctx(explicit_live_enable=False)
        result = evaluate_preflight(ctx)
        assert result.outbound_allowed is False
        assert "explicit_live_enable_required" in result.blocker_reasons

    def test_live_mode_not_enabled_blocked(self):
        ctx = all_clear_ctx(live_mode_enabled=False)
        result = evaluate_preflight(ctx)
        assert result.outbound_allowed is False
        assert "live_mode_not_enabled" in result.blocker_reasons

    def test_credentials_incomplete_blocked(self):
        ctx = all_clear_ctx(credentials_complete=False)
        result = evaluate_preflight(ctx)
        assert result.outbound_allowed is False
        assert "live_credentials_incomplete" in result.blocker_reasons

    def test_verification_not_passed_blocked(self):
        ctx = all_clear_ctx(verification_passed=False)
        result = evaluate_preflight(ctx)
        assert result.outbound_allowed is False
        assert "verification_not_passed" in result.blocker_reasons

    def test_sizing_not_passed_blocked(self):
        ctx = all_clear_ctx(sizing_passed=False)
        result = evaluate_preflight(ctx)
        assert result.outbound_allowed is False
        assert "sizing_not_passed" in result.blocker_reasons

    def test_risk_not_passed_blocked(self):
        ctx = all_clear_ctx(risk_passed=False)
        result = evaluate_preflight(ctx)
        assert result.outbound_allowed is False
        assert "risk_not_passed" in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestMultipleBlockers
# ---------------------------------------------------------------------------

class TestMultipleBlockers:
    def test_two_blockers_returned_together(self):
        ctx = all_clear_ctx(credentials_complete=False, risk_passed=False)
        result = evaluate_preflight(ctx)
        assert result.outbound_allowed is False
        assert "live_credentials_incomplete" in result.blocker_reasons
        assert "risk_not_passed" in result.blocker_reasons
        assert len(result.blocker_reasons) == 2

    def test_all_live_path_blockers_simultaneously(self):
        ctx = all_clear_ctx(
            explicit_live_enable=False,
            live_mode_enabled=False,
            credentials_complete=False,
            verification_passed=False,
            sizing_passed=False,
            risk_passed=False,
        )
        result = evaluate_preflight(ctx)
        assert result.outbound_allowed is False
        assert "explicit_live_enable_required" in result.blocker_reasons
        assert "live_mode_not_enabled" in result.blocker_reasons
        assert "live_credentials_incomplete" in result.blocker_reasons
        assert "verification_not_passed" in result.blocker_reasons
        assert "sizing_not_passed" in result.blocker_reasons
        assert "risk_not_passed" in result.blocker_reasons
        assert len(result.blocker_reasons) == 6

    def test_no_short_circuit_first_block_does_not_stop_checks(self):
        """First failing check must not prevent remaining checks from running."""
        ctx = all_clear_ctx(
            explicit_live_enable=False,  # first check fails
            risk_passed=False,           # last check must still run
        )
        result = evaluate_preflight(ctx)
        assert len(result.blocker_reasons) >= 2
        assert "explicit_live_enable_required" in result.blocker_reasons
        assert "risk_not_passed" in result.blocker_reasons

    def test_blocker_count_matches_violations(self):
        ctx = all_clear_ctx(sizing_passed=False, verification_passed=False)
        result = evaluate_preflight(ctx)
        assert len(result.blocker_reasons) == 2

    def test_outbound_action_type_carried_through(self):
        """outbound_action_type is accessible on context in all scenarios."""
        ctx = all_clear_ctx(outbound_action_type=OutboundActionType.LIVE_CLAIM_SUBMIT)
        result = evaluate_preflight(ctx)
        assert ctx.outbound_action_type == OutboundActionType.LIVE_CLAIM_SUBMIT
        assert result.outbound_allowed is True
