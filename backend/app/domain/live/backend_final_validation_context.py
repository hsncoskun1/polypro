"""Backend final validation context — v0.8.3.

Carries the state of every backend chain link required for final
non-live validation. Used by validate_backend_final_state() to produce
a BackendFinalValidationResult.

live_applied_testing_ready is always controlled externally — it is never
auto-set to True by the validator. This preserves the "backend ready but
live applied testing is a separate phase" invariant.
"""
from dataclasses import dataclass, field


@dataclass
class BackendFinalValidationContext:
    """Full non-live backend validation context.

    Attributes:
        simulation_mode_available: Simulation mode path is ready and valid.
        live_readiness_available: Live readiness evaluation chain is present (v0.7.0).
        credentials_ready: Exchange credentials are complete and valid (v0.7.1).
        outbound_guard_ready: Preflight/outbound guard chain is ready (v0.7.2).
        adapter_ready: LiveExchangeClient adapter is resolved (v0.7.8).
        concrete_client_ready: ProductionExchangeClient is available (v0.8.0).
        hardening_ready: Operational hardening layer is in place (v0.8.1).
        backend_readiness_ready: End-to-end backend readiness chain passed (v0.8.2).
        mock_mode_valid: Live-mock path is correctly configured and valid.
        dry_run_mode_valid: Dry-run path is correctly configured and valid.
        production_wiring_valid: Production wiring path is complete and valid (v0.7.9).
        validation_mode: Active NonLiveValidationMode for this evaluation.
    """
    simulation_mode_available: bool = False
    live_readiness_available: bool = False
    credentials_ready: bool = False
    outbound_guard_ready: bool = False
    adapter_ready: bool = False
    concrete_client_ready: bool = False
    hardening_ready: bool = False
    backend_readiness_ready: bool = False
    mock_mode_valid: bool = False
    dry_run_mode_valid: bool = False
    production_wiring_valid: bool = False
    validation_mode: str = ""
