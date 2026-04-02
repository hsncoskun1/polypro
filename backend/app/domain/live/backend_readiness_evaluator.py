"""Backend readiness evaluator — v0.8.2.

Evaluates a BackendReadinessContext and produces a BackendReadinessResult.

Design rules:
- Every critical chain link is checked in order.
- Any False link adds a blocker reason.
- backend_ready=True only when ALL critical links are True.
- Fail-closed: unknown/incomplete state never treated as ready.
- No network calls, no side effects — pure evaluation.
"""
from typing import List
from app.domain.live.backend_readiness_context import BackendReadinessContext
from app.domain.live.backend_readiness_result import BackendReadinessResult

# Ordered list of (field_name, blocker_reason) for all critical chain links.
_CHAIN_CHECKS = [
    ("live_mode_requested",          "live_mode_not_requested"),
    ("explicit_live_enable",         "explicit_live_enable_missing"),
    ("credentials_complete",         "credentials_incomplete"),
    ("preflight_passed",             "preflight_not_ready"),
    ("outbound_allowed",             "outbound_guard_not_ready"),
    ("production_wiring_ready",      "client_selection_not_ready"),
    ("adapter_available",            "adapter_not_ready"),
    ("concrete_client_available",    "production_client_not_ready"),
    ("submission_ready",             "submission_chain_not_ready"),
    ("response_classification_ready","response_chain_not_ready"),
    ("cancel_replace_ready",         "cancel_replace_chain_not_ready"),
    ("reconciliation_ready",         "reconciliation_not_ready"),
    ("orchestrator_ready",           "orchestrator_not_ready"),
]


def evaluate_backend_readiness(ctx: BackendReadinessContext) -> BackendReadinessResult:
    """Evaluate the end-to-end backend chain and return a readiness result.

    Args:
        ctx: BackendReadinessContext with all chain link flags.

    Returns:
        BackendReadinessResult with backend_ready=True only if all links pass.
    """
    blockers: List[str] = []

    for field_name, reason in _CHAIN_CHECKS:
        if not getattr(ctx, field_name, False):
            blockers.append(reason)

    return BackendReadinessResult(
        backend_ready=(len(blockers) == 0),
        blocker_reasons=blockers,
        client_mode=ctx.client_mode,
    )
