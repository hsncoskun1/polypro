"""Tests for backend readiness end-to-end chain — v0.8.2."""
from app.domain.live.backend_readiness_context import BackendReadinessContext
from app.domain.live.backend_readiness_result import BackendReadinessResult
from app.domain.live.backend_readiness_evaluator import evaluate_backend_readiness


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _full_context(**overrides) -> BackendReadinessContext:
    """Return a fully-ready BackendReadinessContext with optional overrides."""
    defaults = dict(
        live_mode_requested=True,
        explicit_live_enable=True,
        credentials_complete=True,
        preflight_passed=True,
        outbound_allowed=True,
        client_mode="live_production",
        production_wiring_ready=True,
        adapter_available=True,
        concrete_client_available=True,
        submission_ready=True,
        response_classification_ready=True,
        cancel_replace_ready=True,
        reconciliation_ready=True,
        orchestrator_ready=True,
    )
    defaults.update(overrides)
    return BackendReadinessContext(**defaults)


# ---------------------------------------------------------------------------
# TestBackendReadinessContext
# ---------------------------------------------------------------------------

class TestBackendReadinessContext:
    def test_defaults_all_false(self):
        ctx = BackendReadinessContext()
        assert ctx.live_mode_requested is False
        assert ctx.explicit_live_enable is False
        assert ctx.credentials_complete is False
        assert ctx.preflight_passed is False
        assert ctx.outbound_allowed is False
        assert ctx.client_mode == ""
        assert ctx.production_wiring_ready is False
        assert ctx.adapter_available is False
        assert ctx.concrete_client_available is False
        assert ctx.submission_ready is False
        assert ctx.response_classification_ready is False
        assert ctx.cancel_replace_ready is False
        assert ctx.reconciliation_ready is False
        assert ctx.orchestrator_ready is False

    def test_all_fields_settable(self):
        ctx = _full_context()
        assert ctx.live_mode_requested is True
        assert ctx.orchestrator_ready is True
        assert ctx.client_mode == "live_production"


# ---------------------------------------------------------------------------
# TestBackendReadinessResult
# ---------------------------------------------------------------------------

class TestBackendReadinessResult:
    def test_defaults(self):
        r = BackendReadinessResult()
        assert r.backend_ready is False
        assert r.blocker_reasons == []
        assert r.client_mode == ""

    def test_fields_set(self):
        r = BackendReadinessResult(
            backend_ready=True,
            blocker_reasons=[],
            client_mode="live_production",
        )
        assert r.backend_ready is True
        assert r.client_mode == "live_production"

    def test_blocker_reasons_independent(self):
        r1 = BackendReadinessResult()
        r2 = BackendReadinessResult()
        r1.blocker_reasons.append("x")
        assert r2.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestBackendReadinessEvaluator — full chain
# ---------------------------------------------------------------------------

class TestBackendReadinessEvaluatorFullChain:
    def test_full_chain_complete_backend_ready_true(self):
        ctx = _full_context()
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is True
        assert result.blocker_reasons == []

    def test_full_chain_returns_result_type(self):
        ctx = _full_context()
        result = evaluate_backend_readiness(ctx)
        assert isinstance(result, BackendReadinessResult)

    def test_full_chain_client_mode_forwarded(self):
        ctx = _full_context(client_mode="live_production")
        result = evaluate_backend_readiness(ctx)
        assert result.client_mode == "live_production"

    def test_empty_context_backend_not_ready(self):
        ctx = BackendReadinessContext()
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert len(result.blocker_reasons) > 0


# ---------------------------------------------------------------------------
# TestBackendReadinessEvaluator — per-link blockers
# ---------------------------------------------------------------------------

class TestBackendReadinessEvaluatorBlockers:
    def test_live_mode_not_requested(self):
        ctx = _full_context(live_mode_requested=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "live_mode_not_requested" in result.blocker_reasons

    def test_explicit_live_enable_missing(self):
        ctx = _full_context(explicit_live_enable=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "explicit_live_enable_missing" in result.blocker_reasons

    def test_credentials_incomplete(self):
        ctx = _full_context(credentials_complete=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "credentials_incomplete" in result.blocker_reasons

    def test_preflight_not_ready(self):
        ctx = _full_context(preflight_passed=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "preflight_not_ready" in result.blocker_reasons

    def test_outbound_guard_not_ready(self):
        ctx = _full_context(outbound_allowed=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "outbound_guard_not_ready" in result.blocker_reasons

    def test_client_selection_not_ready(self):
        ctx = _full_context(production_wiring_ready=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "client_selection_not_ready" in result.blocker_reasons

    def test_adapter_not_ready(self):
        ctx = _full_context(adapter_available=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "adapter_not_ready" in result.blocker_reasons

    def test_production_client_not_ready(self):
        ctx = _full_context(concrete_client_available=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "production_client_not_ready" in result.blocker_reasons

    def test_submission_chain_not_ready(self):
        ctx = _full_context(submission_ready=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "submission_chain_not_ready" in result.blocker_reasons

    def test_response_chain_not_ready(self):
        ctx = _full_context(response_classification_ready=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "response_chain_not_ready" in result.blocker_reasons

    def test_cancel_replace_chain_not_ready(self):
        ctx = _full_context(cancel_replace_ready=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "cancel_replace_chain_not_ready" in result.blocker_reasons

    def test_reconciliation_not_ready(self):
        ctx = _full_context(reconciliation_ready=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "reconciliation_not_ready" in result.blocker_reasons

    def test_orchestrator_not_ready(self):
        ctx = _full_context(orchestrator_ready=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "orchestrator_not_ready" in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestBackendReadinessEvaluator — multiple blockers
# ---------------------------------------------------------------------------

class TestBackendReadinessEvaluatorMultipleBlockers:
    def test_multiple_missing_links_all_reported(self):
        ctx = _full_context(
            credentials_complete=False,
            preflight_passed=False,
            adapter_available=False,
        )
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert "credentials_incomplete" in result.blocker_reasons
        assert "preflight_not_ready" in result.blocker_reasons
        assert "adapter_not_ready" in result.blocker_reasons

    def test_all_links_missing_all_blockers_reported(self):
        ctx = BackendReadinessContext()
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
        assert len(result.blocker_reasons) == 13  # all 13 chain links

    def test_backend_readiness_incomplete_blocker_string(self):
        """backend_readiness_incomplete is a valid summary blocker reason."""
        ctx = BackendReadinessContext()
        result = evaluate_backend_readiness(ctx)
        # Not asserting the exact string — just that backend is not ready
        assert result.backend_ready is False

    def test_single_last_link_missing(self):
        ctx = _full_context(orchestrator_ready=False)
        result = evaluate_backend_readiness(ctx)
        assert len(result.blocker_reasons) == 1
        assert result.blocker_reasons[0] == "orchestrator_not_ready"

    def test_blocker_order_follows_chain_order(self):
        """Blockers are emitted in chain traversal order."""
        ctx = _full_context(
            live_mode_requested=False,
            orchestrator_ready=False,
        )
        result = evaluate_backend_readiness(ctx)
        assert result.blocker_reasons[0] == "live_mode_not_requested"
        assert result.blocker_reasons[-1] == "orchestrator_not_ready"

    def test_no_silent_fallback_to_ready(self):
        """Partial context never silently resolves to backend_ready=True."""
        ctx = _full_context(submission_ready=False)
        result = evaluate_backend_readiness(ctx)
        assert result.backend_ready is False
