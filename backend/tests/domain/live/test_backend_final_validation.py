"""Tests for backend final integration + safe non-live validation — v0.8.3."""
from app.domain.live.non_live_validation_mode import NonLiveValidationMode
from app.domain.live.backend_final_validation_context import BackendFinalValidationContext
from app.domain.live.backend_final_validation_result import BackendFinalValidationResult
from app.domain.live.backend_final_validator import validate_backend_final_state


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _full_context(**overrides) -> BackendFinalValidationContext:
    """Return a fully-ready BackendFinalValidationContext with optional overrides."""
    defaults = dict(
        simulation_mode_available=True,
        live_readiness_available=True,
        credentials_ready=True,
        outbound_guard_ready=True,
        adapter_ready=True,
        concrete_client_ready=True,
        hardening_ready=True,
        backend_readiness_ready=True,
        mock_mode_valid=True,
        dry_run_mode_valid=True,
        production_wiring_valid=True,
        validation_mode=NonLiveValidationMode.PRODUCTION_WIRING,
    )
    defaults.update(overrides)
    return BackendFinalValidationContext(**defaults)


# ---------------------------------------------------------------------------
# TestNonLiveValidationMode
# ---------------------------------------------------------------------------

class TestNonLiveValidationMode:
    def test_simulation_value(self):
        assert NonLiveValidationMode.SIMULATION == "simulation"

    def test_mock_value(self):
        assert NonLiveValidationMode.MOCK == "mock"

    def test_dry_run_value(self):
        assert NonLiveValidationMode.DRY_RUN == "dry_run"

    def test_production_wiring_value(self):
        assert NonLiveValidationMode.PRODUCTION_WIRING == "production_wiring"

    def test_all_four_modes(self):
        assert len(list(NonLiveValidationMode)) == 4


# ---------------------------------------------------------------------------
# TestBackendFinalValidationContext
# ---------------------------------------------------------------------------

class TestBackendFinalValidationContext:
    def test_defaults_all_false(self):
        ctx = BackendFinalValidationContext()
        assert ctx.simulation_mode_available is False
        assert ctx.live_readiness_available is False
        assert ctx.credentials_ready is False
        assert ctx.outbound_guard_ready is False
        assert ctx.adapter_ready is False
        assert ctx.concrete_client_ready is False
        assert ctx.hardening_ready is False
        assert ctx.backend_readiness_ready is False
        assert ctx.mock_mode_valid is False
        assert ctx.dry_run_mode_valid is False
        assert ctx.production_wiring_valid is False
        assert ctx.validation_mode == ""

    def test_all_fields_settable(self):
        ctx = _full_context()
        assert ctx.simulation_mode_available is True
        assert ctx.production_wiring_valid is True
        assert ctx.validation_mode == NonLiveValidationMode.PRODUCTION_WIRING


# ---------------------------------------------------------------------------
# TestBackendFinalValidationResult
# ---------------------------------------------------------------------------

class TestBackendFinalValidationResult:
    def test_defaults(self):
        r = BackendFinalValidationResult()
        assert r.final_backend_ready is False
        assert r.live_applied_testing_ready is False
        assert r.blocker_reasons == []
        assert r.validation_mode == ""

    def test_blocker_reasons_independent(self):
        r1 = BackendFinalValidationResult()
        r2 = BackendFinalValidationResult()
        r1.blocker_reasons.append("x")
        assert r2.blocker_reasons == []

    def test_live_applied_testing_ready_default_false(self):
        """live_applied_testing_ready must default to False."""
        r = BackendFinalValidationResult(final_backend_ready=True)
        assert r.live_applied_testing_ready is False


# ---------------------------------------------------------------------------
# TestBackendFinalValidator — full chain
# ---------------------------------------------------------------------------

class TestBackendFinalValidatorFullChain:
    def test_full_chain_complete_final_ready_true(self):
        ctx = _full_context()
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is True
        assert result.blocker_reasons == []

    def test_full_chain_returns_result_type(self):
        ctx = _full_context()
        result = validate_backend_final_state(ctx)
        assert isinstance(result, BackendFinalValidationResult)

    def test_full_chain_validation_mode_forwarded(self):
        ctx = _full_context(validation_mode=NonLiveValidationMode.DRY_RUN)
        result = validate_backend_final_state(ctx)
        assert result.validation_mode == NonLiveValidationMode.DRY_RUN

    def test_empty_context_not_final_ready(self):
        ctx = BackendFinalValidationContext()
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert len(result.blocker_reasons) > 0

    def test_final_ready_true_live_testing_still_false(self):
        """Even when final_backend_ready=True, live_applied_testing_ready stays False."""
        ctx = _full_context()
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is True
        assert result.live_applied_testing_ready is False

    def test_live_applied_testing_never_auto_enabled(self):
        """live_applied_testing_ready is never set True by the validator."""
        for _ in range(3):
            ctx = _full_context()
            result = validate_backend_final_state(ctx)
            assert result.live_applied_testing_ready is False


# ---------------------------------------------------------------------------
# TestBackendFinalValidator — per-link blockers
# ---------------------------------------------------------------------------

class TestBackendFinalValidatorBlockers:
    def test_simulation_mode_not_ready(self):
        ctx = _full_context(simulation_mode_available=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "simulation_mode_not_ready" in result.blocker_reasons

    def test_live_readiness_not_ready(self):
        ctx = _full_context(live_readiness_available=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "live_readiness_not_ready" in result.blocker_reasons

    def test_credentials_not_ready(self):
        ctx = _full_context(credentials_ready=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "credentials_not_ready" in result.blocker_reasons

    def test_outbound_guard_not_ready(self):
        ctx = _full_context(outbound_guard_ready=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "outbound_guard_not_ready" in result.blocker_reasons

    def test_adapter_not_ready(self):
        ctx = _full_context(adapter_ready=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "adapter_not_ready" in result.blocker_reasons

    def test_concrete_client_not_ready(self):
        ctx = _full_context(concrete_client_ready=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "concrete_client_not_ready" in result.blocker_reasons

    def test_hardening_not_ready(self):
        ctx = _full_context(hardening_ready=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "hardening_not_ready" in result.blocker_reasons

    def test_backend_readiness_not_ready(self):
        ctx = _full_context(backend_readiness_ready=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "backend_readiness_not_ready" in result.blocker_reasons

    def test_mock_mode_not_valid(self):
        ctx = _full_context(mock_mode_valid=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "mock_mode_not_valid" in result.blocker_reasons

    def test_dry_run_mode_not_valid(self):
        ctx = _full_context(dry_run_mode_valid=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "dry_run_mode_not_valid" in result.blocker_reasons

    def test_production_wiring_not_valid(self):
        ctx = _full_context(production_wiring_valid=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "production_wiring_not_valid" in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestBackendFinalValidator — multiple blockers + order
# ---------------------------------------------------------------------------

class TestBackendFinalValidatorMultipleBlockers:
    def test_multiple_missing_links_all_reported(self):
        ctx = _full_context(
            credentials_ready=False,
            adapter_ready=False,
            hardening_ready=False,
        )
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert "credentials_not_ready" in result.blocker_reasons
        assert "adapter_not_ready" in result.blocker_reasons
        assert "hardening_not_ready" in result.blocker_reasons

    def test_all_links_missing_all_11_blockers_reported(self):
        ctx = BackendFinalValidationContext()
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert len(result.blocker_reasons) == 11

    def test_blocker_order_follows_chain_order(self):
        ctx = _full_context(
            simulation_mode_available=False,
            production_wiring_valid=False,
        )
        result = validate_backend_final_state(ctx)
        assert result.blocker_reasons[0] == "simulation_mode_not_ready"
        assert result.blocker_reasons[-1] == "production_wiring_not_valid"

    def test_single_last_link_missing(self):
        ctx = _full_context(production_wiring_valid=False)
        result = validate_backend_final_state(ctx)
        assert len(result.blocker_reasons) == 1
        assert result.blocker_reasons[0] == "production_wiring_not_valid"

    def test_no_silent_fallback_to_final_ready(self):
        ctx = _full_context(mock_mode_valid=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False

    def test_backend_final_validation_incomplete_when_any_missing(self):
        ctx = _full_context(dry_run_mode_valid=False)
        result = validate_backend_final_state(ctx)
        assert result.final_backend_ready is False
        assert len(result.blocker_reasons) >= 1

    def test_live_applied_testing_not_enabled_even_with_blockers(self):
        ctx = BackendFinalValidationContext()
        result = validate_backend_final_state(ctx)
        assert result.live_applied_testing_ready is False
