"""Live order response classifier — v0.7.4.

classify_order_response(): Determines OrderResponseStatus from raw exchange response data.
build_fill_confirmation(): Derives FillConfirmation read model from LiveOrderResponse.

Trigger / submitted / fill lifecycle is NEVER collapsed.
"""
from app.domain.live.fill_confirmation import FillConfirmation
from app.domain.live.fill_confirmation_status import FillConfirmationStatus
from app.domain.live.live_order_response import LiveOrderResponse
from app.domain.live.order_response_status import OrderResponseStatus


def classify_order_response(
    order_id: str,
    requested_size: float,
    accepted_size: float = 0.0,
    filled_size: float = 0.0,
    exchange_acknowledged: bool = False,
    rejected: bool = False,
    retryable: bool = False,
    terminal_failure: bool = False,
    reject_reason: str = "",
    response_received_at: str = "",
    fill_confirmed_at: str = "",
) -> LiveOrderResponse:
    """Classify a live order response based on exchange-returned state.

    Priority order:
      1. terminal_failure → TERMINAL_FAILURE
      2. retryable        → RETRYABLE_FAILURE
      3. rejected         → REJECTED
      4. filled_size >= requested_size → FILLED
      5. filled_size > 0  → PARTIALLY_FILLED
      6. exchange_acknowledged → ACCEPTED
      7. default          → SUBMITTED
    """
    remaining = max(0.0, requested_size - filled_size)

    if terminal_failure:
        status = OrderResponseStatus.TERMINAL_FAILURE
    elif retryable:
        status = OrderResponseStatus.RETRYABLE_FAILURE
    elif rejected:
        status = OrderResponseStatus.REJECTED
    elif filled_size >= requested_size:
        status = OrderResponseStatus.FILLED
    elif filled_size > 0:
        status = OrderResponseStatus.PARTIALLY_FILLED
    elif exchange_acknowledged:
        status = OrderResponseStatus.ACCEPTED
    else:
        status = OrderResponseStatus.SUBMITTED

    return LiveOrderResponse(
        order_id=order_id,
        order_response_status=status,
        requested_size=requested_size,
        accepted_size=accepted_size,
        filled_size=filled_size,
        remaining_size=remaining,
        retryable=retryable,
        terminal_failure=terminal_failure,
        reject_reason=reject_reason,
        response_received_at=response_received_at,
        fill_confirmed_at=fill_confirmed_at,
    )


def build_fill_confirmation(response: LiveOrderResponse) -> FillConfirmation:
    """Derive FillConfirmation read model from a LiveOrderResponse.

    Fill confirmation lifecycle:
      confirmation_failed  → CONFIRMATION_FAILED
      filled_size >= requested → FULLY_CONFIRMED
      0 < filled_size < requested → PARTIALLY_CONFIRMED
      filled_size == 0 → NOT_CONFIRMED
    """
    if response.terminal_failure or response.order_response_status == OrderResponseStatus.TERMINAL_FAILURE:
        fill_status = FillConfirmationStatus.CONFIRMATION_FAILED
    elif response.filled_size >= response.requested_size and response.requested_size > 0:
        fill_status = FillConfirmationStatus.FULLY_CONFIRMED
    elif response.filled_size > 0:
        fill_status = FillConfirmationStatus.PARTIALLY_CONFIRMED
    else:
        fill_status = FillConfirmationStatus.NOT_CONFIRMED

    return FillConfirmation(
        order_id=response.order_id,
        fill_confirmation_status=fill_status,
        requested_size=response.requested_size,
        filled_size=response.filled_size,
        remaining_size=response.remaining_size,
        fill_confirmed_at=response.fill_confirmed_at,
    )
