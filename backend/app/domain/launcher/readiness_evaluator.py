"""Launcher readiness evaluator.

Reads ReadinessState and produces a ReadinessResult.
Fail-closed: access_allowed is True only when zero blockers remain.
This is not UI gating — the access decision is authoritative here.
"""
from app.domain.launcher.readiness_result import ReadinessResult
from app.domain.launcher.readiness_state import ReadinessState


def evaluate_readiness(state: ReadinessState) -> ReadinessResult:
    """Evaluate launcher readiness and return an access decision.

    Blocker reasons:
    - setup_not_completed   → setup_completed is False
    - update_required       → update_required is True
    - preflight_not_passed  → preflight_passed is False
    """
    blockers: list[str] = []

    if not state.setup_completed:
        blockers.append("setup_not_completed")

    if state.update_required:
        blockers.append("update_required")

    if not state.preflight_passed:
        blockers.append("preflight_not_passed")

    return ReadinessResult(
        access_allowed=len(blockers) == 0,
        blocker_reasons=blockers,
    )
