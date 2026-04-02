"""Live test gate evaluator — v0.8.4.

Evaluates LiveTestGateContext → LiveTestGateResult.

Design invariants:
- live_applied_testing_ready=True ONLY when all three gate conditions pass.
- release_ready alone is NOT sufficient — gate must also be explicitly enabled
  and passed.
- Fail-closed: any missing gate condition blocks live applied testing.
- live_applied_testing_ready is never auto-propagated from release_ready.
"""
from typing import List
from app.domain.live.live_test_gate_context import LiveTestGateContext
from app.domain.live.live_test_gate_result import LiveTestGateResult

_GATE_CHECKS = [
    ("release_ready",          "release_readiness_incomplete"),
    ("live_test_gate_enabled", "live_test_gate_disabled"),
    ("live_test_gate_passed",  "live_test_gate_not_passed"),
]


def evaluate_live_test_gate(ctx: LiveTestGateContext) -> LiveTestGateResult:
    """Evaluate the live test gate.

    Args:
        ctx: LiveTestGateContext.

    Returns:
        LiveTestGateResult.
        live_applied_testing_ready=True only if ALL gate conditions pass.
        Never auto-enabled — release_ready alone is not sufficient.
    """
    blockers: List[str] = []

    for field_name, reason in _GATE_CHECKS:
        if not getattr(ctx, field_name, False):
            blockers.append(reason)

    return LiveTestGateResult(
        live_applied_testing_ready=(len(blockers) == 0),
        blocker_reasons=blockers,
    )
