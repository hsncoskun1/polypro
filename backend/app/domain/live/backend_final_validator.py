"""Backend final validator — v0.8.3.

Validates the full non-live backend chain and produces a BackendFinalValidationResult.

Design rules:
- Every critical chain link is checked in order.
- Any False link adds a blocker reason.
- final_backend_ready=True only when ALL critical links pass.
- live_applied_testing_ready is NEVER set to True by this validator.
  It is always False — live applied testing is a separate authorization step.
- Fail-closed: unknown/incomplete state never treated as final-ready.
- No network calls, no side effects — pure evaluation.
"""
from typing import List
from app.domain.live.backend_final_validation_context import BackendFinalValidationContext
from app.domain.live.backend_final_validation_result import BackendFinalValidationResult

# Ordered list of (field_name, blocker_reason) for all critical chain links.
_FINAL_CHAIN_CHECKS = [
    ("simulation_mode_available", "simulation_mode_not_ready"),
    ("live_readiness_available",  "live_readiness_not_ready"),
    ("credentials_ready",         "credentials_not_ready"),
    ("outbound_guard_ready",      "outbound_guard_not_ready"),
    ("adapter_ready",             "adapter_not_ready"),
    ("concrete_client_ready",     "concrete_client_not_ready"),
    ("hardening_ready",           "hardening_not_ready"),
    ("backend_readiness_ready",   "backend_readiness_not_ready"),
    ("mock_mode_valid",           "mock_mode_not_valid"),
    ("dry_run_mode_valid",        "dry_run_mode_not_valid"),
    ("production_wiring_valid",   "production_wiring_not_valid"),
]


def validate_backend_final_state(
    ctx: BackendFinalValidationContext,
) -> BackendFinalValidationResult:
    """Validate the full non-live backend chain.

    Args:
        ctx: BackendFinalValidationContext with all chain link flags.

    Returns:
        BackendFinalValidationResult.
        final_backend_ready=True only if all 11 links pass.
        live_applied_testing_ready is always False (separate authorization step).
    """
    blockers: List[str] = []

    for field_name, reason in _FINAL_CHAIN_CHECKS:
        if not getattr(ctx, field_name, False):
            blockers.append(reason)

    return BackendFinalValidationResult(
        final_backend_ready=(len(blockers) == 0),
        live_applied_testing_ready=False,  # never auto-enabled
        blocker_reasons=blockers,
        validation_mode=ctx.validation_mode,
    )
