"""Live order event reconciler — v0.7.6.

reconcile_order_events(): Applies a sequence of LiveOrderEvents to produce
a final LiveOrderState and LiveOrderReconciliationResult.

Design decisions:
- No events → ReconciliationStatus.NO_EVENTS, no final state
- Events applied in order supplied (caller is responsible for ordering)
- Idempotent application seam: each event updates state, no deduplication engine
- Terminal events: ORDER_FILLED, ORDER_CANCELLED, ORDER_REJECTED, ORDER_EXPIRED, ORDER_FAILED
- Once terminal, further events still processed but is_terminal flag preserved
- Separate from websocket/client — seam only
"""
from typing import List
from app.domain.live.live_order_event import LiveOrderEvent
from app.domain.live.live_order_event_type import LiveOrderEventType
from app.domain.live.live_order_reconciliation_result import LiveOrderReconciliationResult
from app.domain.live.live_order_state import LiveOrderState
from app.domain.live.reconciliation_status import ReconciliationStatus


_TERMINAL_EVENT_TYPES = frozenset({
    LiveOrderEventType.ORDER_FILLED,
    LiveOrderEventType.ORDER_CANCELLED,
    LiveOrderEventType.ORDER_REJECTED,
    LiveOrderEventType.ORDER_EXPIRED,
    LiveOrderEventType.ORDER_FAILED,
})


def _is_terminal_event(event_type: LiveOrderEventType) -> bool:
    return event_type in _TERMINAL_EVENT_TYPES


def _apply_event(state: LiveOrderState, event: LiveOrderEvent) -> LiveOrderState:
    """Apply a single event to produce an updated state (returns same object mutated)."""
    state.current_event_type = event.event_type
    state.event_count += 1

    if event.event_timestamp:
        state.last_event_timestamp = event.event_timestamp
    if event.client_order_id:
        state.client_order_id = event.client_order_id
    if event.side:
        state.side = event.side
    if event.requested_size:
        state.requested_size = event.requested_size
    if event.limit_price:
        state.limit_price = event.limit_price
    if event.filled_size:
        state.filled_size = event.filled_size
    if event.remaining_size is not None and event.remaining_size > 0:
        state.remaining_size = event.remaining_size

    event_type = event.event_type

    if event_type == LiveOrderEventType.ORDER_FILLED:
        state.is_filled = True
        state.is_terminal = True
        if state.requested_size and not state.filled_size:
            state.filled_size = state.requested_size
        state.remaining_size = 0.0

    elif event_type == LiveOrderEventType.ORDER_PARTIALLY_FILLED:
        state.is_filled = False

    elif event_type == LiveOrderEventType.ORDER_CANCELLED:
        state.is_cancelled = True
        state.is_terminal = True

    elif event_type in (
        LiveOrderEventType.ORDER_REJECTED,
        LiveOrderEventType.ORDER_EXPIRED,
        LiveOrderEventType.ORDER_FAILED,
    ):
        state.is_terminal = True

    elif event_type == LiveOrderEventType.ORDER_REPLACED:
        # Replace: update price/size from event fields
        pass  # fields already updated above

    return state


def reconcile_order_events(
    order_id: str,
    events: List[LiveOrderEvent],
) -> LiveOrderReconciliationResult:
    """Reconcile a list of events into a final order state.

    Args:
        order_id: The order reference being reconciled.
        events: Ordered list of LiveOrderEvent records.

    Returns:
        LiveOrderReconciliationResult with final state and reconciliation status.
    """
    if not events:
        return LiveOrderReconciliationResult(
            order_id=order_id,
            reconciliation_status=ReconciliationStatus.NO_EVENTS,
            final_state=None,
            events_processed=0,
            is_terminal=False,
        )

    state = LiveOrderState(order_id=order_id)

    for event in events:
        state = _apply_event(state, event)

    status = (
        ReconciliationStatus.TERMINAL_STATE
        if state.is_terminal
        else ReconciliationStatus.RECONCILED
    )

    return LiveOrderReconciliationResult(
        order_id=order_id,
        reconciliation_status=status,
        final_state=state,
        events_processed=len(events),
        is_terminal=state.is_terminal,
    )
