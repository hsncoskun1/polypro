"""Non-live validation mode enum — v0.8.3."""
from enum import Enum


class NonLiveValidationMode(str, Enum):
    """Validation mode used during safe non-live backend validation.

    Values:
        SIMULATION: Simulation mode — no live execution, mock fills.
        MOCK: Live-mock mode — live path selected but mock client used.
        DRY_RUN: Dry-run mode — wiring ready, outbound blocked for safety.
        PRODUCTION_WIRING: Production wiring mode — all live components wired,
            awaiting live applied testing authorization.
    """
    SIMULATION = "simulation"
    MOCK = "mock"
    DRY_RUN = "dry_run"
    PRODUCTION_WIRING = "production_wiring"
