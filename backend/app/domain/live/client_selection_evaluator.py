"""Client selection evaluator — v0.7.9.

evaluate_client_selection(): Determines whether the wiring is ready,
whether real outbound is allowed, and whether dry-run mode is active.

Client mode resolution:
  SIMULATION_MOCK  → ready, no real outbound
  LIVE_MOCK        → ready, no real outbound (live path, mock adapter)
  LIVE_DRY_RUN     → ready only if production_wiring_ready, dry_run_active=True, no real outbound
  LIVE_PRODUCTION  → ready only if outbound_execution_enabled + production_client_selected +
                     production_wiring_ready; real outbound allowed

Blocker reason vocabulary:
  production_client_not_selected
  production_wiring_incomplete
  dry_run_mode_active
  real_outbound_disabled
  client_selection_invalid
  production_client_ready  (not a blocker — informational; not emitted)
"""
from app.domain.live.client_mode import ClientMode
from app.domain.live.client_wiring_context import ClientWiringContext
from app.domain.live.client_wiring_result import ClientWiringResult


def evaluate_client_selection(ctx: ClientWiringContext) -> ClientWiringResult:
    """Evaluate client wiring context and return wiring readiness result."""

    if ctx.client_mode == ClientMode.SIMULATION_MOCK:
        return ClientWiringResult(
            client_mode=ctx.client_mode,
            client_ready=True,
            real_outbound_allowed=False,
        )

    if ctx.client_mode == ClientMode.LIVE_MOCK:
        return ClientWiringResult(
            client_mode=ctx.client_mode,
            client_ready=True,
            real_outbound_allowed=False,
        )

    if ctx.client_mode == ClientMode.LIVE_DRY_RUN:
        blockers = []
        if not ctx.production_wiring_ready:
            blockers.append("production_wiring_incomplete")
        if blockers:
            return ClientWiringResult(
                client_mode=ctx.client_mode,
                client_ready=False,
                real_outbound_allowed=False,
                dry_run_active=False,
                blocker_reasons=blockers,
            )
        return ClientWiringResult(
            client_mode=ctx.client_mode,
            client_ready=True,
            real_outbound_allowed=False,
            dry_run_active=True,
            blocker_reasons=["dry_run_mode_active"],
        )

    if ctx.client_mode == ClientMode.LIVE_PRODUCTION:
        blockers = []
        if not ctx.outbound_execution_enabled:
            blockers.append("real_outbound_disabled")
        if not ctx.production_client_selected:
            blockers.append("production_client_not_selected")
        if not ctx.production_wiring_ready:
            blockers.append("production_wiring_incomplete")
        if blockers:
            return ClientWiringResult(
                client_mode=ctx.client_mode,
                client_ready=False,
                real_outbound_allowed=False,
                blocker_reasons=blockers,
            )
        return ClientWiringResult(
            client_mode=ctx.client_mode,
            client_ready=True,
            real_outbound_allowed=True,
        )

    # Unknown mode
    return ClientWiringResult(
        client_mode=ctx.client_mode,
        client_ready=False,
        real_outbound_allowed=False,
        blocker_reasons=["client_selection_invalid"],
    )
