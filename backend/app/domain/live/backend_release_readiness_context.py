"""Backend release readiness context — v0.8.4."""
from dataclasses import dataclass


@dataclass
class BackendReleaseReadinessContext:
    """Context for backend release readiness evaluation.

    Derives from the non-live backend chain. All critical links must
    be True for release_ready to be granted.

    Attributes:
        final_backend_ready: v0.8.3 final non-live validation passed.
        production_wiring_valid: v0.7.9 production wiring is valid.
        hardening_ready: v0.8.1 operational hardening is in place.
        adapter_ready: v0.7.8 adapter is resolved.
        concrete_client_ready: v0.8.0 concrete client is available.
        validation_mode_ready: A valid NonLiveValidationMode is set.
    """
    final_backend_ready: bool = False
    production_wiring_valid: bool = False
    hardening_ready: bool = False
    adapter_ready: bool = False
    concrete_client_ready: bool = False
    validation_mode_ready: bool = False
