"""Live execution preflight evaluator — v0.7.2.

Fail-closed: outbound_allowed is True only when ALL conditions pass.

Gate model:
  Gate 1: simulation default (not live requested)
          → blocked with outbound_not_allowed_in_simulation (single reason, clean)
  Gate 2+: all remaining checks run (no short-circuit)
           → all active blockers collected and returned together

Blocker reasons:
  outbound_not_allowed_in_simulation  — simulation default, live not requested
  explicit_live_enable_required       — explicit live enable flag not set
  live_mode_not_enabled               — live mode not currently enabled
  live_credentials_incomplete         — one or more credentials missing
  verification_not_passed             — verification gate failed
  sizing_not_passed                   — sizing gate failed
  risk_not_passed                     — risk gate failed
"""
from app.domain.live.preflight_context import PreflightContext
from app.domain.live.preflight_result import PreflightResult


def evaluate_preflight(ctx: PreflightContext) -> PreflightResult:
    # Gate 1: simulation default — single clean blocker, no further checks
    if ctx.simulation_mode_default and not ctx.live_mode_requested:
        return PreflightResult(
            outbound_allowed=False,
            blocker_reasons=["outbound_not_allowed_in_simulation"],
        )

    # Gate 2+: all checks run — no short-circuit
    blockers = []

    if not ctx.explicit_live_enable:
        blockers.append("explicit_live_enable_required")
    if not ctx.live_mode_enabled:
        blockers.append("live_mode_not_enabled")
    if not ctx.credentials_complete:
        blockers.append("live_credentials_incomplete")
    if not ctx.verification_passed:
        blockers.append("verification_not_passed")
    if not ctx.sizing_passed:
        blockers.append("sizing_not_passed")
    if not ctx.risk_passed:
        blockers.append("risk_not_passed")

    return PreflightResult(
        outbound_allowed=len(blockers) == 0,
        blocker_reasons=blockers,
    )
