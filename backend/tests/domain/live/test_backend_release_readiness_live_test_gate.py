"""Tests for backend release readiness + live test gate — v0.8.4."""
from app.domain.live.backend_release_readiness_context import BackendReleaseReadinessContext
from app.domain.live.backend_release_readiness_result import BackendReleaseReadinessResult
from app.domain.live.backend_release_readiness_evaluator import evaluate_release_readiness
from app.domain.live.live_test_gate_context import LiveTestGateContext
from app.domain.live.live_test_gate_result import LiveTestGateResult
from app.domain.live.live_test_gate_evaluator import evaluate_live_test_gate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _full_release_ctx(**overrides) -> BackendReleaseReadinessContext:
    defaults = dict(
        final_backend_ready=True,
        production_wiring_valid=True,
        hardening_ready=True,
        adapter_ready=True,
        concrete_client_ready=True,
        validation_mode_ready=True,
    )
    defaults.update(overrides)
    return BackendReleaseReadinessContext(**defaults)


def _full_gate_ctx(**overrides) -> LiveTestGateContext:
    defaults = dict(
        release_ready=True,
        live_test_gate_enabled=True,
        live_test_gate_passed=True,
    )
    defaults.update(overrides)
    return LiveTestGateContext(**defaults)


# ---------------------------------------------------------------------------
# TestBackendReleaseReadinessContext
# ---------------------------------------------------------------------------

class TestBackendReleaseReadinessContext:
    def test_defaults_all_false(self):
        ctx = BackendReleaseReadinessContext()
        assert ctx.final_backend_ready is False
        assert ctx.production_wiring_valid is False
        assert ctx.hardening_ready is False
        assert ctx.adapter_ready is False
        assert ctx.concrete_client_ready is False
        assert ctx.validation_mode_ready is False

    def test_all_fields_settable(self):
        ctx = _full_release_ctx()
        assert ctx.final_backend_ready is True
        assert ctx.validation_mode_ready is True


# ---------------------------------------------------------------------------
# TestBackendReleaseReadinessResult
# ---------------------------------------------------------------------------

class TestBackendReleaseReadinessResult:
    def test_defaults(self):
        r = BackendReleaseReadinessResult()
        assert r.release_ready is False
        assert r.blocker_reasons == []

    def test_blocker_reasons_independent(self):
        r1 = BackendReleaseReadinessResult()
        r2 = BackendReleaseReadinessResult()
        r1.blocker_reasons.append("x")
        assert r2.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestLiveTestGateContext
# ---------------------------------------------------------------------------

class TestLiveTestGateContext:
    def test_defaults_all_false(self):
        ctx = LiveTestGateContext()
        assert ctx.release_ready is False
        assert ctx.live_test_gate_enabled is False
        assert ctx.live_test_gate_passed is False

    def test_all_fields_settable(self):
        ctx = _full_gate_ctx()
        assert ctx.release_ready is True
        assert ctx.live_test_gate_enabled is True
        assert ctx.live_test_gate_passed is True


# ---------------------------------------------------------------------------
# TestLiveTestGateResult
# ---------------------------------------------------------------------------

class TestLiveTestGateResult:
    def test_defaults(self):
        r = LiveTestGateResult()
        assert r.live_applied_testing_ready is False
        assert r.blocker_reasons == []

    def test_blocker_reasons_independent(self):
        r1 = LiveTestGateResult()
        r2 = LiveTestGateResult()
        r1.blocker_reasons.append("x")
        assert r2.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestReleaseReadinessEvaluator — full chain
# ---------------------------------------------------------------------------

class TestReleaseReadinessEvaluatorFullChain:
    def test_full_chain_release_ready_true(self):
        ctx = _full_release_ctx()
        result = evaluate_release_readiness(ctx)
        assert result.release_ready is True
        assert result.blocker_reasons == []

    def test_returns_result_type(self):
        result = evaluate_release_readiness(_full_release_ctx())
        assert isinstance(result, BackendReleaseReadinessResult)

    def test_empty_context_not_ready(self):
        ctx = BackendReleaseReadinessContext()
        result = evaluate_release_readiness(ctx)
        assert result.release_ready is False
        assert len(result.blocker_reasons) == 6


# ---------------------------------------------------------------------------
# TestReleaseReadinessEvaluator — per-link blockers
# ---------------------------------------------------------------------------

class TestReleaseReadinessEvaluatorBlockers:
    def test_final_backend_not_ready(self):
        ctx = _full_release_ctx(final_backend_ready=False)
        result = evaluate_release_readiness(ctx)
        assert result.release_ready is False
        assert "final_backend_not_ready" in result.blocker_reasons

    def test_production_wiring_not_valid(self):
        ctx = _full_release_ctx(production_wiring_valid=False)
        result = evaluate_release_readiness(ctx)
        assert result.release_ready is False
        assert "production_wiring_not_valid" in result.blocker_reasons

    def test_hardening_not_ready(self):
        ctx = _full_release_ctx(hardening_ready=False)
        result = evaluate_release_readiness(ctx)
        assert result.release_ready is False
        assert "hardening_not_ready" in result.blocker_reasons

    def test_adapter_not_ready(self):
        ctx = _full_release_ctx(adapter_ready=False)
        result = evaluate_release_readiness(ctx)
        assert result.release_ready is False
        assert "adapter_not_ready" in result.blocker_reasons

    def test_concrete_client_not_ready(self):
        ctx = _full_release_ctx(concrete_client_ready=False)
        result = evaluate_release_readiness(ctx)
        assert result.release_ready is False
        assert "concrete_client_not_ready" in result.blocker_reasons

    def test_validation_mode_not_ready(self):
        ctx = _full_release_ctx(validation_mode_ready=False)
        result = evaluate_release_readiness(ctx)
        assert result.release_ready is False
        assert "validation_mode_not_ready" in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestLiveTestGateEvaluator — full gate
# ---------------------------------------------------------------------------

class TestLiveTestGateEvaluatorFullGate:
    def test_full_gate_live_testing_ready(self):
        ctx = _full_gate_ctx()
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is True
        assert result.blocker_reasons == []

    def test_returns_result_type(self):
        result = evaluate_live_test_gate(_full_gate_ctx())
        assert isinstance(result, LiveTestGateResult)

    def test_empty_gate_context_not_ready(self):
        ctx = LiveTestGateContext()
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is False
        assert len(result.blocker_reasons) == 3

    def test_release_ready_alone_insufficient(self):
        """release_ready=True alone does NOT grant live_applied_testing_ready."""
        ctx = LiveTestGateContext(release_ready=True)
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is False
        assert "live_test_gate_disabled" in result.blocker_reasons

    def test_release_and_gate_enabled_but_not_passed(self):
        ctx = LiveTestGateContext(release_ready=True, live_test_gate_enabled=True)
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is False
        assert "live_test_gate_not_passed" in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestLiveTestGateEvaluator — per-gate blockers
# ---------------------------------------------------------------------------

class TestLiveTestGateEvaluatorBlockers:
    def test_release_readiness_incomplete(self):
        ctx = _full_gate_ctx(release_ready=False)
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is False
        assert "release_readiness_incomplete" in result.blocker_reasons

    def test_live_test_gate_disabled(self):
        ctx = _full_gate_ctx(live_test_gate_enabled=False)
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is False
        assert "live_test_gate_disabled" in result.blocker_reasons

    def test_live_test_gate_not_passed(self):
        ctx = _full_gate_ctx(live_test_gate_passed=False)
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is False
        assert "live_test_gate_not_passed" in result.blocker_reasons

    def test_live_applied_testing_not_authorized_when_all_missing(self):
        ctx = LiveTestGateContext()
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is False
        assert len(result.blocker_reasons) == 3


# ---------------------------------------------------------------------------
# TestReleaseAndGateSeparation — key invariants
# ---------------------------------------------------------------------------

class TestReleaseAndGateSeparation:
    def test_release_ready_does_not_imply_live_testing_ready(self):
        """release_ready=True + gate disabled → live_applied_testing_ready=False."""
        release_ctx = _full_release_ctx()
        release_result = evaluate_release_readiness(release_ctx)
        assert release_result.release_ready is True

        gate_ctx = LiveTestGateContext(
            release_ready=release_result.release_ready,
            live_test_gate_enabled=False,
            live_test_gate_passed=False,
        )
        gate_result = evaluate_live_test_gate(gate_ctx)
        assert gate_result.live_applied_testing_ready is False

    def test_both_ready_grants_live_testing(self):
        """release_ready=True + gate fully enabled → live_applied_testing_ready=True."""
        release_ctx = _full_release_ctx()
        release_result = evaluate_release_readiness(release_ctx)

        gate_ctx = _full_gate_ctx(release_ready=release_result.release_ready)
        gate_result = evaluate_live_test_gate(gate_ctx)
        assert gate_result.live_applied_testing_ready is True

    def test_release_and_gate_are_independent_evaluations(self):
        release_result = evaluate_release_readiness(_full_release_ctx())
        gate_result = evaluate_live_test_gate(_full_gate_ctx())
        assert isinstance(release_result, BackendReleaseReadinessResult)
        assert isinstance(gate_result, LiveTestGateResult)

    def test_blocker_order_follows_gate_chain(self):
        ctx = LiveTestGateContext()
        result = evaluate_live_test_gate(ctx)
        assert result.blocker_reasons[0] == "release_readiness_incomplete"
        assert result.blocker_reasons[-1] == "live_test_gate_not_passed"

    def test_no_silent_fallback_to_live_testing(self):
        ctx = _full_gate_ctx(live_test_gate_passed=False)
        result = evaluate_live_test_gate(ctx)
        assert result.live_applied_testing_ready is False
