"""Live execution driver — v1.0.4.

Orchestrates a single live order execution cycle:
  submit → fill-stream poll loop → reconcile → orchestrate → accounting summary.

All sub-layer components are injectable for testing.
No live testing. No automatic outbound. Fail-closed throughout.

Flow:
  1. Guard check (outbound_allowed + preflight_passed).
  2. Submit via LiveExchangeClient.submit_order().
  3. Poll loop via PolymarketHttpClient.execute_get_fill_stream_update().
  4. Convert fill stream results to LiveOrderEvents.
  5. Reconcile events via reconcile_order_events().
  6. Build orchestration context from sub-layer results.
  7. Resolve stage via orchestrate_live_execution().
  8. Build accounting summary from fill data.
  9. Return LiveExecutionDriverResult.

Fail-closed rules:
  - outbound_allowed=False or preflight_passed=False → PREFLIGHT_BLOCKED immediately.
  - Submit terminal_failure → TERMINAL_FAILURE, no polling.
  - Submit retryable → RETRYABLE_FAILURE, no polling.
  - Poll terminal_failure (auth error / malformed) → TERMINAL_FAILURE, stop polling.
  - Poll retryable (timeout / 5xx / 429) → RETRYABLE_FAILURE, stop polling.
  - update_type="unknown" → TERMINAL_FAILURE, stop polling.
  - No fake success at any step.
"""
import time
from typing import Optional

from app.domain.live.live_execution_driver_context import LiveExecutionDriverContext
from app.domain.live.live_execution_driver_result import LiveExecutionDriverResult
from app.domain.live.live_exchange_client import LiveExchangeClient
from app.domain.live.polymarket_http_client import PolymarketHttpClient
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.production_exchange_client import ProductionExchangeClient
from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus
from app.domain.live.adapter_submit_response import AdapterSubmitResponse
from app.domain.live.order_fill_stream_payload import OrderFillStreamPayload
from app.domain.live.order_fill_stream_result import OrderFillStreamResult
from app.domain.live.live_order_event import LiveOrderEvent
from app.domain.live.live_order_event_type import LiveOrderEventType
from app.domain.live.live_order_reconciliation_result import LiveOrderReconciliationResult
from app.domain.live.order_event_reconciler import reconcile_order_events
from app.domain.live.live_execution_orchestration_context import LiveExecutionOrchestrationContext
from app.domain.live.live_execution_orchestrator import orchestrate_live_execution
from app.domain.live.live_execution_stage import LiveExecutionStage
from app.domain.accounting.accounting_context import AccountingContext
from app.domain.accounting.accounting_snapshot import AccountingSnapshot
from app.domain.accounting.entry_fill_accounting import compute_entry_fill_accounting

_UPDATE_TYPE_TO_EVENT_TYPE: dict[str, LiveOrderEventType] = {
    "full_fill": LiveOrderEventType.ORDER_FILLED,
    "partial_fill": LiveOrderEventType.ORDER_PARTIALLY_FILLED,
    "cancelled": LiveOrderEventType.ORDER_CANCELLED,
    "rejected": LiveOrderEventType.ORDER_REJECTED,
}

_TERMINAL_UPDATE_TYPES: frozenset[str] = frozenset({"full_fill", "cancelled", "rejected"})

_SUBMITTED_STATUSES: frozenset[AdapterOutcomeStatus] = frozenset({
    AdapterOutcomeStatus.ADAPTER_SUBMITTED,
    AdapterOutcomeStatus.ADAPTER_ACCEPTED,
})


class LiveExecutionDriver:
    """Runs a single live execution cycle from submit through reconciliation.

    All sub-layer components are injectable. Default instances used when None.
    """

    def __init__(
        self,
        exchange_client: LiveExchangeClient | None = None,
        http_client: PolymarketHttpClient | None = None,
        credentials: LiveCredentials | None = None,
    ) -> None:
        self._exchange_client = exchange_client or ProductionExchangeClient()
        self._http_client = http_client or PolymarketHttpClient()
        self._credentials = credentials or LiveCredentials()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, ctx: LiveExecutionDriverContext) -> LiveExecutionDriverResult:
        """Execute a complete live order lifecycle cycle.

        Args:
            ctx: LiveExecutionDriverContext with submit request, credentials,
                 guards, and polling configuration.

        Returns:
            LiveExecutionDriverResult with all sub-layer results and stage.
        """
        # Step 1: Guard check
        if not ctx.outbound_allowed or not ctx.preflight_passed:
            return self._blocked_result(ctx)

        # Step 2: Submit
        submit_response = self._exchange_client.submit_order(ctx.submit_request)
        trace = [f"submit:{submit_response.outcome_status}"]

        if submit_response.terminal_failure:
            return LiveExecutionDriverResult(
                event_key=ctx.event_key,
                order_id=ctx.submit_request.order_id,
                client_order_id=ctx.submit_request.event_key,
                submit_result=submit_response.outcome_status.value,
                driver_stage=LiveExecutionStage.TERMINAL_FAILURE.value,
                terminal_failure=True,
                raw_driver_trace=trace,
            )

        if submit_response.retryable:
            return LiveExecutionDriverResult(
                event_key=ctx.event_key,
                order_id=ctx.submit_request.order_id,
                client_order_id=ctx.submit_request.event_key,
                submit_result=submit_response.outcome_status.value,
                driver_stage=LiveExecutionStage.RETRYABLE_FAILURE.value,
                retryable=True,
                raw_driver_trace=trace,
            )

        order_id = submit_response.exchange_order_id or ctx.submit_request.order_id

        # Step 3: Poll loop
        events: list[LiveOrderEvent] = []
        poll_attempts = 0
        last_update_status = ""
        last_fill_price = 0.0
        last_filled_size = 0.0
        poll_terminal = False
        poll_retryable = False

        for i in range(ctx.max_poll_attempts):
            if ctx.poll_delay_seconds > 0:
                time.sleep(ctx.poll_delay_seconds)
            poll_attempts += 1
            fill_payload = OrderFillStreamPayload(
                order_id=order_id,
                client_order_id=ctx.submit_request.event_key,
            )
            fill_result = self._http_client.execute_get_fill_stream_update(
                fill_payload, self._credentials
            )
            trace.append(f"poll_{i + 1}:{fill_result.update_type}")
            last_update_status = fill_result.update_type

            if fill_result.terminal_failure:
                poll_terminal = True
                trace.append(f"poll_terminal:{fill_result.reject_reason}")
                break

            if fill_result.retryable:
                poll_retryable = True
                trace.append(f"poll_retryable:{fill_result.reject_reason}")
                break

            if fill_result.update_type == "unknown":
                poll_terminal = True
                trace.append("poll_terminal:unknown_update_type")
                break

            event = self._to_live_order_event(
                fill_result, order_id, ctx.submit_request.event_key
            )
            if event is not None:
                events.append(event)
                if fill_result.filled_size > 0:
                    last_fill_price = fill_result.fill_price
                    last_filled_size = fill_result.filled_size

            if fill_result.update_type in _TERMINAL_UPDATE_TYPES:
                break

        if poll_terminal:
            return LiveExecutionDriverResult(
                event_key=ctx.event_key,
                order_id=order_id,
                client_order_id=ctx.submit_request.event_key,
                submit_result=submit_response.outcome_status.value,
                update_result=last_update_status,
                driver_stage=LiveExecutionStage.TERMINAL_FAILURE.value,
                terminal_failure=True,
                poll_attempts=poll_attempts,
                last_update_status=last_update_status,
                raw_driver_trace=trace,
            )

        if poll_retryable:
            return LiveExecutionDriverResult(
                event_key=ctx.event_key,
                order_id=order_id,
                client_order_id=ctx.submit_request.event_key,
                submit_result=submit_response.outcome_status.value,
                update_result=last_update_status,
                driver_stage=LiveExecutionStage.RETRYABLE_FAILURE.value,
                retryable=True,
                poll_attempts=poll_attempts,
                last_update_status=last_update_status,
                raw_driver_trace=trace,
            )

        # Step 4: Reconcile events
        reconcile_result = reconcile_order_events(order_id, events)
        trace.append(f"reconcile:{reconcile_result.reconciliation_status}")

        # Step 5: Build orchestration context
        orch_ctx = self._build_orchestration_ctx(
            ctx, order_id, submit_response, reconcile_result
        )

        # Step 6: Orchestrate stage
        orch_result = orchestrate_live_execution(orch_ctx)
        trace.append(f"stage:{orch_result.current_stage}")

        # Step 7: Accounting summary
        if last_filled_size > 0:
            accounting_ctx = AccountingContext(
                side=ctx.submit_request.side,
                entry_trigger_price=last_fill_price,
                entry_order_submitted_price=ctx.submit_request.limit_price,
                entry_fill_price=last_fill_price,
                current_price=last_fill_price,
                requested_size=ctx.submit_request.size,
                filled_size=last_filled_size,
                total_balance=0.0,
                available_balance=0.0,
                session_start_balance=0.0,
            )
            accounting_result: AccountingSnapshot = compute_entry_fill_accounting(accounting_ctx)
        else:
            accounting_result = AccountingSnapshot(
                side=ctx.submit_request.side,
                entry_trigger_price=0.0,
                entry_order_submitted_price=0.0,
                entry_fill_price=0.0,
                entry_trigger_move_value=0.0,
                entry_fill_move_value=0.0,
                current_price=0.0,
                current_move_value=0.0,
                exit_trigger_price=0.0,
                exit_order_submitted_price=0.0,
                exit_fill_price=0.0,
                requested_size=ctx.submit_request.size,
                filled_size=0.0,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                session_realized_pnl=0.0,
                session_unrealized_pnl=0.0,
                session_total_pnl=0.0,
                total_balance=0.0,
                available_balance=0.0,
                session_start_balance=0.0,
                current_balance=0.0,
                claim_adjusted_balance_effect=0.0,
            )

        return LiveExecutionDriverResult(
            event_key=ctx.event_key,
            order_id=order_id,
            client_order_id=ctx.submit_request.event_key,
            submit_result=submit_response.outcome_status.value,
            update_result=last_update_status,
            reconciliation_result=reconcile_result.reconciliation_status.value,
            accounting_result=accounting_result,
            driver_stage=orch_result.current_stage.value,
            completed=orch_result.orchestration_completed,
            retryable=orch_result.retryable,
            terminal_failure=orch_result.terminal_failure,
            blocker_reasons=list(orch_result.blocker_reasons),
            poll_attempts=poll_attempts,
            last_update_status=last_update_status,
            last_fill_price=last_fill_price,
            last_filled_size=last_filled_size,
            realized_pnl=accounting_result.realized_pnl,
            unrealized_pnl=accounting_result.unrealized_pnl,
            current_balance=accounting_result.current_balance,
            raw_driver_trace=trace,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _blocked_result(self, ctx: LiveExecutionDriverContext) -> LiveExecutionDriverResult:
        reasons = []
        if not ctx.outbound_allowed:
            reasons.append("outbound_not_allowed")
        if not ctx.preflight_passed:
            reasons.append("preflight_not_passed")
        return LiveExecutionDriverResult(
            event_key=ctx.event_key,
            order_id=ctx.submit_request.order_id,
            client_order_id=ctx.submit_request.event_key,
            driver_stage=LiveExecutionStage.PREFLIGHT_BLOCKED.value,
            terminal_failure=False,
            retryable=False,
            completed=False,
            blocker_reasons=reasons,
            raw_driver_trace=[f"blocked:{','.join(reasons)}"],
        )

    def _build_orchestration_ctx(
        self,
        ctx: LiveExecutionDriverContext,
        order_id: str,
        submit_response: AdapterSubmitResponse,
        reconcile_result: LiveOrderReconciliationResult,
    ) -> LiveExecutionOrchestrationContext:
        final_state = reconcile_result.final_state

        # submission_status
        if submit_response.outcome_status in _SUBMITTED_STATUSES:
            submission_status = "submission_submitted"
        else:
            submission_status = ""

        # fill_confirmation_status
        if final_state and final_state.is_filled:
            fill_confirmation_status = "fully_confirmed"
        elif final_state and final_state.filled_size > 0:
            fill_confirmation_status = "partially_confirmed"
        else:
            fill_confirmation_status = ""

        # cancel_status
        if final_state and final_state.is_cancelled:
            cancel_status = "cancel_cancelled"
        else:
            cancel_status = ""

        # terminal_failure — rejected orders
        terminal_failure = bool(
            final_state
            and final_state.is_terminal
            and not final_state.is_filled
            and not final_state.is_cancelled
        )

        return LiveExecutionOrchestrationContext(
            event_key=ctx.event_key,
            order_id=order_id,
            live_mode_requested=True,
            outbound_allowed=ctx.outbound_allowed,
            preflight_passed=ctx.preflight_passed,
            submission_status=submission_status,
            fill_confirmation_status=fill_confirmation_status,
            cancel_status=cancel_status,
            terminal_failure=terminal_failure,
        )

    @staticmethod
    def _to_live_order_event(
        fill_result: OrderFillStreamResult,
        order_id: str,
        client_order_id: str,
    ) -> Optional[LiveOrderEvent]:
        """Convert OrderFillStreamResult to LiveOrderEvent. Returns None for no_update."""
        event_type = _UPDATE_TYPE_TO_EVENT_TYPE.get(fill_result.update_type)
        if event_type is None:
            return None
        return LiveOrderEvent(
            order_id=order_id,
            event_type=event_type,
            client_order_id=client_order_id,
            event_timestamp=fill_result.updated_at,
            filled_size=fill_result.filled_size,
            remaining_size=fill_result.remaining_size,
            limit_price=fill_result.fill_price,
        )
