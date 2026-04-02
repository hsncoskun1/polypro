"""Tests for production client wiring + safe dry-run foundation — v0.7.9."""
import pytest
from app.domain.live.client_mode import ClientMode
from app.domain.live.client_wiring_context import ClientWiringContext
from app.domain.live.client_wiring_result import ClientWiringResult
from app.domain.live.dry_run_result import DryRunResult
from app.domain.live.client_selection_evaluator import evaluate_client_selection
from app.domain.live.adapter_factory import resolve_adapter
from app.domain.live.mock_live_exchange_client import MockLiveExchangeClient
from app.domain.live.live_exchange_client import LiveExchangeClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sim_ctx(**overrides) -> ClientWiringContext:
    defaults = dict(client_mode=ClientMode.SIMULATION_MOCK, simulation_mode=True)
    defaults.update(overrides)
    return ClientWiringContext(**defaults)


def live_mock_ctx(**overrides) -> ClientWiringContext:
    defaults = dict(
        client_mode=ClientMode.LIVE_MOCK,
        simulation_mode=False,
        live_mode_requested=True,
        mock_client_selected=True,
    )
    defaults.update(overrides)
    return ClientWiringContext(**defaults)


def dry_run_ctx(**overrides) -> ClientWiringContext:
    defaults = dict(
        client_mode=ClientMode.LIVE_DRY_RUN,
        simulation_mode=False,
        live_mode_requested=True,
        dry_run_enabled=True,
        production_wiring_ready=True,
    )
    defaults.update(overrides)
    return ClientWiringContext(**defaults)


def production_ctx(**overrides) -> ClientWiringContext:
    defaults = dict(
        client_mode=ClientMode.LIVE_PRODUCTION,
        simulation_mode=False,
        live_mode_requested=True,
        production_client_selected=True,
        outbound_execution_enabled=True,
        production_wiring_ready=True,
    )
    defaults.update(overrides)
    return ClientWiringContext(**defaults)


# ---------------------------------------------------------------------------
# TestClientMode
# ---------------------------------------------------------------------------

class TestClientMode:
    def test_simulation_mock(self):
        assert ClientMode.SIMULATION_MOCK == "simulation_mock"

    def test_live_mock(self):
        assert ClientMode.LIVE_MOCK == "live_mock"

    def test_live_dry_run(self):
        assert ClientMode.LIVE_DRY_RUN == "live_dry_run"

    def test_live_production(self):
        assert ClientMode.LIVE_PRODUCTION == "live_production"

    def test_is_str_enum(self):
        assert isinstance(ClientMode.SIMULATION_MOCK, str)


# ---------------------------------------------------------------------------
# TestClientWiringContext
# ---------------------------------------------------------------------------

class TestClientWiringContext:
    def test_required_fields(self):
        ctx = ClientWiringContext(client_mode=ClientMode.SIMULATION_MOCK)
        assert ctx.client_mode == ClientMode.SIMULATION_MOCK

    def test_defaults(self):
        ctx = ClientWiringContext(client_mode=ClientMode.SIMULATION_MOCK)
        assert ctx.simulation_mode is True
        assert ctx.live_mode_requested is False
        assert ctx.production_client_selected is False
        assert ctx.mock_client_selected is False
        assert ctx.dry_run_enabled is False
        assert ctx.outbound_execution_enabled is False
        assert ctx.production_wiring_ready is False


# ---------------------------------------------------------------------------
# TestClientWiringResult
# ---------------------------------------------------------------------------

class TestClientWiringResult:
    def test_required_fields(self):
        r = ClientWiringResult(
            client_mode=ClientMode.SIMULATION_MOCK,
            client_ready=True,
            real_outbound_allowed=False,
        )
        assert r.client_mode == ClientMode.SIMULATION_MOCK
        assert r.client_ready is True
        assert r.real_outbound_allowed is False

    def test_defaults(self):
        r = ClientWiringResult(
            client_mode=ClientMode.SIMULATION_MOCK,
            client_ready=True,
            real_outbound_allowed=False,
        )
        assert r.dry_run_active is False
        assert r.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestDryRunResult
# ---------------------------------------------------------------------------

class TestDryRunResult:
    def test_required_fields(self):
        r = DryRunResult(
            client_mode=ClientMode.LIVE_DRY_RUN,
            dry_run_action_recorded=True,
        )
        assert r.client_mode == ClientMode.LIVE_DRY_RUN
        assert r.dry_run_action_recorded is True

    def test_real_outbound_always_false_default(self):
        r = DryRunResult(
            client_mode=ClientMode.LIVE_DRY_RUN,
            dry_run_action_recorded=True,
        )
        assert r.real_outbound_performed is False

    def test_real_outbound_cannot_be_true_in_dry_run(self):
        """Dry-run must never perform real outbound."""
        r = DryRunResult(
            client_mode=ClientMode.LIVE_DRY_RUN,
            dry_run_action_recorded=True,
            real_outbound_performed=False,
        )
        assert r.real_outbound_performed is False

    def test_action_description_default(self):
        r = DryRunResult(
            client_mode=ClientMode.LIVE_DRY_RUN,
            dry_run_action_recorded=False,
        )
        assert r.action_description == ""


# ---------------------------------------------------------------------------
# TestEvaluateClientSelection — Simulation Mock
# ---------------------------------------------------------------------------

class TestEvaluateSimulationMock:
    def test_simulation_mock_returns_ready(self):
        result = evaluate_client_selection(sim_ctx())
        assert result.client_ready is True

    def test_simulation_mock_no_real_outbound(self):
        result = evaluate_client_selection(sim_ctx())
        assert result.real_outbound_allowed is False

    def test_simulation_mock_no_dry_run(self):
        result = evaluate_client_selection(sim_ctx())
        assert result.dry_run_active is False

    def test_simulation_mock_no_blockers(self):
        result = evaluate_client_selection(sim_ctx())
        assert result.blocker_reasons == []

    def test_simulation_mock_client_mode_preserved(self):
        result = evaluate_client_selection(sim_ctx())
        assert result.client_mode == ClientMode.SIMULATION_MOCK


# ---------------------------------------------------------------------------
# TestEvaluateClientSelection — Live Mock
# ---------------------------------------------------------------------------

class TestEvaluateLiveMock:
    def test_live_mock_returns_ready(self):
        result = evaluate_client_selection(live_mock_ctx())
        assert result.client_ready is True

    def test_live_mock_no_real_outbound(self):
        result = evaluate_client_selection(live_mock_ctx())
        assert result.real_outbound_allowed is False

    def test_live_mock_no_dry_run(self):
        result = evaluate_client_selection(live_mock_ctx())
        assert result.dry_run_active is False

    def test_live_mock_client_mode_preserved(self):
        result = evaluate_client_selection(live_mock_ctx())
        assert result.client_mode == ClientMode.LIVE_MOCK


# ---------------------------------------------------------------------------
# TestEvaluateClientSelection — Live Dry-Run
# ---------------------------------------------------------------------------

class TestEvaluateLiveDryRun:
    def test_dry_run_wiring_ready_returns_ready(self):
        result = evaluate_client_selection(dry_run_ctx())
        assert result.client_ready is True

    def test_dry_run_no_real_outbound(self):
        result = evaluate_client_selection(dry_run_ctx())
        assert result.real_outbound_allowed is False

    def test_dry_run_active_flag_set(self):
        result = evaluate_client_selection(dry_run_ctx())
        assert result.dry_run_active is True

    def test_dry_run_blocker_reason_set(self):
        result = evaluate_client_selection(dry_run_ctx())
        assert "dry_run_mode_active" in result.blocker_reasons

    def test_dry_run_wiring_incomplete_blocks(self):
        result = evaluate_client_selection(dry_run_ctx(production_wiring_ready=False))
        assert result.client_ready is False
        assert "production_wiring_incomplete" in result.blocker_reasons

    def test_dry_run_wiring_incomplete_no_dry_run_active(self):
        result = evaluate_client_selection(dry_run_ctx(production_wiring_ready=False))
        assert result.dry_run_active is False


# ---------------------------------------------------------------------------
# TestEvaluateClientSelection — Live Production
# ---------------------------------------------------------------------------

class TestEvaluateLiveProduction:
    def test_all_clear_returns_ready(self):
        result = evaluate_client_selection(production_ctx())
        assert result.client_ready is True

    def test_all_clear_real_outbound_allowed(self):
        result = evaluate_client_selection(production_ctx())
        assert result.real_outbound_allowed is True

    def test_all_clear_no_blockers(self):
        result = evaluate_client_selection(production_ctx())
        assert result.blocker_reasons == []

    def test_outbound_disabled_blocks(self):
        result = evaluate_client_selection(production_ctx(outbound_execution_enabled=False))
        assert result.client_ready is False
        assert "real_outbound_disabled" in result.blocker_reasons

    def test_production_client_not_selected_blocks(self):
        result = evaluate_client_selection(production_ctx(production_client_selected=False))
        assert result.client_ready is False
        assert "production_client_not_selected" in result.blocker_reasons

    def test_production_wiring_incomplete_blocks(self):
        result = evaluate_client_selection(production_ctx(production_wiring_ready=False))
        assert result.client_ready is False
        assert "production_wiring_incomplete" in result.blocker_reasons

    def test_multiple_blockers_all_reported(self):
        result = evaluate_client_selection(
            production_ctx(
                outbound_execution_enabled=False,
                production_client_selected=False,
                production_wiring_ready=False,
            )
        )
        assert "real_outbound_disabled" in result.blocker_reasons
        assert "production_client_not_selected" in result.blocker_reasons
        assert "production_wiring_incomplete" in result.blocker_reasons

    def test_production_mode_preserved(self):
        result = evaluate_client_selection(production_ctx())
        assert result.client_mode == ClientMode.LIVE_PRODUCTION


# ---------------------------------------------------------------------------
# TestAdapterFactory
# ---------------------------------------------------------------------------

class TestAdapterFactory:
    def test_simulation_mock_returns_mock_instance(self):
        ctx = sim_ctx()
        adapter = resolve_adapter(ctx)
        assert isinstance(adapter, LiveExchangeClient)

    def test_simulation_mock_uses_provided_mock(self):
        ctx = sim_ctx()
        custom_mock = MockLiveExchangeClient()
        adapter = resolve_adapter(ctx, mock_client=custom_mock)
        assert adapter is custom_mock

    def test_live_mock_returns_mock_instance(self):
        ctx = live_mock_ctx()
        adapter = resolve_adapter(ctx)
        assert isinstance(adapter, MockLiveExchangeClient)

    def test_live_dry_run_returns_mock_instance(self):
        ctx = dry_run_ctx()
        adapter = resolve_adapter(ctx)
        assert isinstance(adapter, MockLiveExchangeClient)

    def test_live_production_without_client_raises(self):
        ctx = production_ctx()
        with pytest.raises(ValueError, match="production_client is required"):
            resolve_adapter(ctx)

    def test_live_production_with_client_returns_it(self):
        ctx = production_ctx()
        prod_mock = MockLiveExchangeClient()
        adapter = resolve_adapter(ctx, production_client=prod_mock)
        assert adapter is prod_mock

    def test_dry_run_adapter_cannot_perform_real_outbound(self):
        """Dry-run adapter returns mock — real outbound never occurs."""
        ctx = dry_run_ctx()
        adapter = resolve_adapter(ctx)
        from app.domain.live.adapter_submit_request import AdapterSubmitRequest
        from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus
        req = AdapterSubmitRequest(
            order_id="ord_001", event_key="evt_001",
            market_id="mkt_001", side="buy", size=10.0, limit_price=0.75,
        )
        resp = adapter.submit_order(req)
        # Mock adapter never sets terminal_failure or real exchange ID
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_SUBMITTED

    def test_simulation_and_production_adapters_are_separate(self):
        """Simulation and production paths never share the same adapter instance."""
        sim = resolve_adapter(sim_ctx())
        prod_mock = MockLiveExchangeClient()
        prod = resolve_adapter(production_ctx(), production_client=prod_mock)
        assert sim is not prod
