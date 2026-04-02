"""Production request mapper — v0.8.0.

Maps internal adapter request contracts to external exchange payload models.
No network calls — pure transformation layer.
"""
from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.adapter_cancel_request import AdapterCancelRequest
from app.domain.live.adapter_replace_request import AdapterReplaceRequest
from app.domain.live.external_submit_payload import ExternalSubmitPayload
from app.domain.live.external_cancel_payload import ExternalCancelPayload
from app.domain.live.external_replace_payload import ExternalReplacePayload


class ProductionRequestMapper:
    """Maps internal adapter requests to external exchange payloads."""

    def map_submit_request(self, request: AdapterSubmitRequest) -> ExternalSubmitPayload:
        return ExternalSubmitPayload(
            order_id=request.order_id,
            market_id=request.market_id,
            side=request.side,
            size=request.size,
            limit_price=request.limit_price,
            client_order_id=request.event_key,
        )

    def map_cancel_request(self, request: AdapterCancelRequest) -> ExternalCancelPayload:
        return ExternalCancelPayload(
            order_id=request.order_id,
            client_order_id=request.event_key,
        )

    def map_replace_request(self, request: AdapterReplaceRequest) -> ExternalReplacePayload:
        return ExternalReplacePayload(
            order_id=request.order_id,
            new_limit_price=request.new_limit_price,
            new_size=request.new_size,
            client_order_id=request.event_key,
        )
