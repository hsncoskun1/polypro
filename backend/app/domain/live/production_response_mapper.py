"""Production response mapper — v0.8.0.

Maps external exchange response payloads to internal adapter response contracts.
No network calls — pure transformation layer.
"""
from app.domain.live.external_response_payload import ExternalResponsePayload
from app.domain.live.adapter_submit_response import AdapterSubmitResponse
from app.domain.live.adapter_cancel_response import AdapterCancelResponse
from app.domain.live.adapter_replace_response import AdapterReplaceResponse
from app.domain.live.adapter_order_update import AdapterOrderUpdate
from app.domain.live.adapter_error_translator import translate_status


class ProductionResponseMapper:
    """Maps external exchange payloads to internal adapter response contracts."""

    def map_submit_response(
        self,
        payload: ExternalResponsePayload,
        order_id: str,
    ) -> AdapterSubmitResponse:
        outcome = translate_status(
            payload.mapped_status,
            terminal_failure=payload.terminal_failure,
            retryable=payload.retryable,
        )
        return AdapterSubmitResponse(
            order_id=order_id,
            outcome_status=outcome,
            exchange_order_id=payload.mapped_order_id,
            reject_reason=payload.mapped_reject_reason,
            retryable=payload.retryable,
            terminal_failure=payload.terminal_failure,
        )

    def map_cancel_response(
        self,
        payload: ExternalResponsePayload,
        order_id: str,
    ) -> AdapterCancelResponse:
        outcome = translate_status(
            payload.mapped_status,
            terminal_failure=payload.terminal_failure,
            retryable=payload.retryable,
        )
        return AdapterCancelResponse(
            order_id=order_id,
            outcome_status=outcome,
            reject_reason=payload.mapped_reject_reason,
            retryable=payload.retryable,
            terminal_failure=payload.terminal_failure,
        )

    def map_replace_response(
        self,
        payload: ExternalResponsePayload,
        order_id: str,
    ) -> AdapterReplaceResponse:
        outcome = translate_status(
            payload.mapped_status,
            terminal_failure=payload.terminal_failure,
            retryable=payload.retryable,
        )
        return AdapterReplaceResponse(
            order_id=order_id,
            outcome_status=outcome,
            new_exchange_order_id=payload.mapped_order_id,
            reject_reason=payload.mapped_reject_reason,
            retryable=payload.retryable,
            terminal_failure=payload.terminal_failure,
        )

    def map_order_update(
        self,
        payload: ExternalResponsePayload,
        order_id: str,
    ) -> AdapterOrderUpdate:
        outcome = translate_status(
            payload.mapped_status,
            terminal_failure=payload.terminal_failure,
            retryable=payload.retryable,
        )
        return AdapterOrderUpdate(
            order_id=order_id,
            outcome_status=outcome,
            filled_size=payload.filled_size,
            remaining_size=payload.remaining_size,
            update_timestamp=payload.received_at,
        )
