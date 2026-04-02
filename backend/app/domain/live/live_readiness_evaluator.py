"""Live readiness evaluator — v0.7.0.

Sequential gate model:
  Gate 1: simulation default → not live_ready, no blockers
  Gate 2: explicit_live_enable required
  Gate 3: credentials (wallet, keys, relayer, API)

All credential checks run — no short-circuit.
"""
from app.domain.live.live_readiness_context import LiveReadinessContext
from app.domain.live.live_readiness_result import LiveReadinessResult


def evaluate_live_readiness(ctx: LiveReadinessContext) -> LiveReadinessResult:
    # Gate 1: simulation default — not live_ready, no blockers
    if ctx.simulation_mode_default and not ctx.live_mode_requested:
        return LiveReadinessResult(live_ready=False, blocker_reasons=[])

    # Gate 2: explicit live enable required
    if not ctx.explicit_live_enable:
        return LiveReadinessResult(
            live_ready=False,
            blocker_reasons=["explicit_live_enable_required"],
        )

    # Gate 3: all credential checks run (no short-circuit)
    blockers = []

    if not ctx.wallet_address_present:
        blockers.append("wallet_address_missing")
    if not ctx.api_key_present:
        blockers.append("api_key_missing")
    if not ctx.api_secret_present:
        blockers.append("api_secret_missing")
    if not ctx.api_passphrase_present:
        blockers.append("api_passphrase_missing")
    if not ctx.private_key_present:
        blockers.append("private_key_missing")
    if not ctx.funder_address_present:
        blockers.append("funder_address_missing")
    if not ctx.relayer_api_present:
        blockers.append("relayer_api_missing")

    return LiveReadinessResult(
        live_ready=len(blockers) == 0,
        blocker_reasons=blockers,
    )
