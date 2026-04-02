"""Backend release readiness evaluator — v0.8.4.

Evaluates BackendReleaseReadinessContext → BackendReleaseReadinessResult.
Fail-closed: any missing link emits a blocker reason, release_ready stays False.
"""
from typing import List
from app.domain.live.backend_release_readiness_context import BackendReleaseReadinessContext
from app.domain.live.backend_release_readiness_result import BackendReleaseReadinessResult

_RELEASE_CHAIN_CHECKS = [
    ("final_backend_ready",    "final_backend_not_ready"),
    ("production_wiring_valid","production_wiring_not_valid"),
    ("hardening_ready",        "hardening_not_ready"),
    ("adapter_ready",          "adapter_not_ready"),
    ("concrete_client_ready",  "concrete_client_not_ready"),
    ("validation_mode_ready",  "validation_mode_not_ready"),
]


def evaluate_release_readiness(
    ctx: BackendReleaseReadinessContext,
) -> BackendReleaseReadinessResult:
    """Evaluate backend release readiness.

    Args:
        ctx: BackendReleaseReadinessContext.

    Returns:
        BackendReleaseReadinessResult with release_ready=True only if all links pass.
    """
    blockers: List[str] = []

    for field_name, reason in _RELEASE_CHAIN_CHECKS:
        if not getattr(ctx, field_name, False):
            blockers.append(reason)

    return BackendReleaseReadinessResult(
        release_ready=(len(blockers) == 0),
        blocker_reasons=blockers,
    )
