"""Mock live exchange client adapter — v0.7.8.

Stub implementation of LiveExchangeClient for testing.
Configurable outcome per operation type. No network calls.
"""
from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus
from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.adapter_submit_response import AdapterSubmitResponse
from app.domain.live.adapter_cancel_request import AdapterCancelRequest
from app.domain.live.adapter_cancel_response import AdapterCancelResponse
from app.domain.live.adapter_replace_request import AdapterReplaceRequest
from app.domain.live.adapter_replace_response import AdapterReplaceResponse
from app.domain.live.adapter_order_update import AdapterOrderUpdate
from app.domain.live.live_exchange_client import LiveExchangeClient


class MockLiveExchangeClient(LiveExchangeClient):
    """Configurable mock adapter for testing orchestrator/business logic.

    Args:
        submit_outcome: Outcome status returned by submit_order()
        cancel_outcome: Outcome status returned by cancel_order()
        replace_outcome: Outcome status returned by replace_order()
        update_outcome: Outcome status returned by get_order_update()
        reject_reason: Optional reason string for rejected outcomes
        retryable: Whether to flag retryable on failure responses
        terminal_failure: Whether to flag terminal_failure on failure responses
    """

    def __init__(
        self,
        submit_outcome: AdapterOutcomeStatus = AdapterOutcomeStatus.ADAPTER_SUBMITTED,
        cancel_outcome: AdapterOutcomeStatus = AdapterOutcomeStatus.ADAPTER_ACCEPTED,
        replace_outcome: AdapterOutcomeStatus = AdapterOutcomeStatus.ADAPTER_SUBMITTED,
        update_outcome: AdapterOutcomeStatus = AdapterOutcomeStatus.ADAPTER_NO_UPDATE,
        reject_reason: str = "",
        retryable: bool = False,
        terminal_failure: bool = False,
    ):
        self.submit_outcome = submit_outcome
        self.cancel_outcome = cancel_outcome
        self.replace_outcome = replace_outcome
        self.update_outcome = update_outcome
        self.reject_reason = reject_reason
        self.retryable = retryable
        self.terminal_failure = terminal_failure

    def submit_order(self, request: AdapterSubmitRequest) -> AdapterSubmitResponse:
        return AdapterSubmitResponse(
            order_id=request.order_id,
            outcome_status=self.submit_outcome,
            reject_reason=self.reject_reason,
            retryable=self.retryable,
            terminal_failure=self.terminal_failure,
        )

    def cancel_order(self, request: AdapterCancelRequest) -> AdapterCancelResponse:
        return AdapterCancelResponse(
            order_id=request.order_id,
            outcome_status=self.cancel_outcome,
            reject_reason=self.reject_reason,
            retryable=self.retryable,
            terminal_failure=self.terminal_failure,
        )

    def replace_order(self, request: AdapterReplaceRequest) -> AdapterReplaceResponse:
        return AdapterReplaceResponse(
            order_id=request.order_id,
            outcome_status=self.replace_outcome,
            reject_reason=self.reject_reason,
            retryable=self.retryable,
            terminal_failure=self.terminal_failure,
        )

    def get_order_update(self, order_id: str) -> AdapterOrderUpdate:
        return AdapterOrderUpdate(
            order_id=order_id,
            outcome_status=self.update_outcome,
        )
