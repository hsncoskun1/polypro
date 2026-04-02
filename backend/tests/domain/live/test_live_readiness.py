"""Tests for live readiness evaluator — v0.7.0."""
from app.domain.live.live_mode import LiveMode
from app.domain.live.live_readiness_context import LiveReadinessContext
from app.domain.live.live_readiness_result import LiveReadinessResult
from app.domain.live.live_readiness_evaluator import evaluate_live_readiness


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def simulation_ctx(**overrides) -> LiveReadinessContext:
    """Default simulation context — all credentials absent, no live request."""
    defaults = dict(
        simulation_mode_default=True,
        live_mode_requested=False,
        live_mode_enabled=False,
        explicit_live_enable=False,
        wallet_address_present=False,
        private_key_present=False,
        funder_address_present=False,
        relayer_api_present=False,
        api_key_present=False,
        api_secret_present=False,
        api_passphrase_present=False,
    )
    defaults.update(overrides)
    return LiveReadinessContext(**defaults)


def live_ready_ctx(**overrides) -> LiveReadinessContext:
    """All prerequisites met for live mode."""
    defaults = dict(
        simulation_mode_default=False,
        live_mode_requested=True,
        live_mode_enabled=True,
        explicit_live_enable=True,
        wallet_address_present=True,
        private_key_present=True,
        funder_address_present=True,
        relayer_api_present=True,
        api_key_present=True,
        api_secret_present=True,
        api_passphrase_present=True,
    )
    defaults.update(overrides)
    return LiveReadinessContext(**defaults)


# ---------------------------------------------------------------------------
# TestLiveModeEnum
# ---------------------------------------------------------------------------

class TestLiveModeEnum:
    def test_simulation_value(self):
        assert LiveMode.SIMULATION == "simulation"

    def test_live_value(self):
        assert LiveMode.LIVE == "live"

    def test_is_str_enum(self):
        assert isinstance(LiveMode.SIMULATION, str)
        assert isinstance(LiveMode.LIVE, str)


# ---------------------------------------------------------------------------
# TestLiveReadinessResult
# ---------------------------------------------------------------------------

class TestLiveReadinessResult:
    def test_live_ready_true_fields(self):
        result = LiveReadinessResult(live_ready=True, blocker_reasons=[])
        assert result.live_ready is True
        assert result.blocker_reasons == []

    def test_live_ready_false_fields(self):
        result = LiveReadinessResult(live_ready=False, blocker_reasons=["explicit_live_enable_required"])
        assert result.live_ready is False
        assert "explicit_live_enable_required" in result.blocker_reasons

    def test_blocker_reasons_default_empty(self):
        result = LiveReadinessResult(live_ready=False)
        assert result.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestSimulationDefault
# ---------------------------------------------------------------------------

class TestSimulationDefault:
    def test_simulation_default_not_live_ready(self):
        result = evaluate_live_readiness(simulation_ctx())
        assert result.live_ready is False

    def test_simulation_default_no_blockers(self):
        """Simulation default should produce no blocker reasons — not a blocked state."""
        result = evaluate_live_readiness(simulation_ctx())
        assert result.blocker_reasons == []

    def test_simulation_default_ignores_credentials(self):
        """Credentials do not matter in simulation default mode."""
        ctx = simulation_ctx(
            wallet_address_present=True,
            api_key_present=True,
            api_secret_present=True,
            api_passphrase_present=True,
            private_key_present=True,
            funder_address_present=True,
            relayer_api_present=True,
        )
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert result.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestExplicitLiveEnable
# ---------------------------------------------------------------------------

class TestExplicitLiveEnable:
    def test_live_requested_without_explicit_enable_blocked(self):
        ctx = simulation_ctx(
            simulation_mode_default=False,
            live_mode_requested=True,
            explicit_live_enable=False,
        )
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "explicit_live_enable_required" in result.blocker_reasons

    def test_explicit_enable_required_is_only_blocker(self):
        ctx = simulation_ctx(
            simulation_mode_default=False,
            live_mode_requested=True,
            explicit_live_enable=False,
        )
        result = evaluate_live_readiness(ctx)
        assert result.blocker_reasons == ["explicit_live_enable_required"]

    def test_explicit_enable_gates_credential_checks(self):
        """With explicit_live_enable=False, credential blockers must NOT appear."""
        ctx = simulation_ctx(
            simulation_mode_default=False,
            live_mode_requested=True,
            explicit_live_enable=False,
            wallet_address_present=False,
            api_key_present=False,
        )
        result = evaluate_live_readiness(ctx)
        assert "wallet_address_missing" not in result.blocker_reasons
        assert "api_key_missing" not in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestCredentialBlockers
# ---------------------------------------------------------------------------

class TestCredentialBlockers:
    def test_all_credentials_present_live_ready(self):
        result = evaluate_live_readiness(live_ready_ctx())
        assert result.live_ready is True
        assert result.blocker_reasons == []

    def test_wallet_address_missing_blocked(self):
        ctx = live_ready_ctx(wallet_address_present=False)
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "wallet_address_missing" in result.blocker_reasons

    def test_api_key_missing_blocked(self):
        ctx = live_ready_ctx(api_key_present=False)
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "api_key_missing" in result.blocker_reasons

    def test_api_secret_missing_blocked(self):
        ctx = live_ready_ctx(api_secret_present=False)
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "api_secret_missing" in result.blocker_reasons

    def test_api_passphrase_missing_blocked(self):
        ctx = live_ready_ctx(api_passphrase_present=False)
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "api_passphrase_missing" in result.blocker_reasons

    def test_private_key_missing_blocked(self):
        ctx = live_ready_ctx(private_key_present=False)
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "private_key_missing" in result.blocker_reasons

    def test_funder_address_missing_blocked(self):
        ctx = live_ready_ctx(funder_address_present=False)
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "funder_address_missing" in result.blocker_reasons

    def test_relayer_api_missing_blocked(self):
        ctx = live_ready_ctx(relayer_api_present=False)
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "relayer_api_missing" in result.blocker_reasons


# ---------------------------------------------------------------------------
# TestMultipleCredentialBlockers
# ---------------------------------------------------------------------------

class TestMultipleCredentialBlockers:
    def test_all_credentials_missing_all_blockers_returned(self):
        ctx = live_ready_ctx(
            wallet_address_present=False,
            api_key_present=False,
            api_secret_present=False,
            api_passphrase_present=False,
            private_key_present=False,
            funder_address_present=False,
            relayer_api_present=False,
        )
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "wallet_address_missing" in result.blocker_reasons
        assert "api_key_missing" in result.blocker_reasons
        assert "api_secret_missing" in result.blocker_reasons
        assert "api_passphrase_missing" in result.blocker_reasons
        assert "private_key_missing" in result.blocker_reasons
        assert "funder_address_missing" in result.blocker_reasons
        assert "relayer_api_missing" in result.blocker_reasons
        assert len(result.blocker_reasons) == 7

    def test_two_credentials_missing_two_blockers(self):
        ctx = live_ready_ctx(wallet_address_present=False, api_key_present=False)
        result = evaluate_live_readiness(ctx)
        assert len(result.blocker_reasons) == 2
        assert "wallet_address_missing" in result.blocker_reasons
        assert "api_key_missing" in result.blocker_reasons

    def test_credential_checks_no_short_circuit(self):
        """First missing credential must not prevent remaining checks."""
        ctx = live_ready_ctx(
            wallet_address_present=False,
            private_key_present=False,
            relayer_api_present=False,
        )
        result = evaluate_live_readiness(ctx)
        assert len(result.blocker_reasons) >= 3
        assert "wallet_address_missing" in result.blocker_reasons
        assert "private_key_missing" in result.blocker_reasons
        assert "relayer_api_missing" in result.blocker_reasons
