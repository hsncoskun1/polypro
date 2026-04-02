"""Production exchange client — concrete implementation — v0.8.0.

Concrete implementation of LiveExchangeClient for production use.
Maps internal adapter contracts to external payloads and back.

This version models the correct integration structure but does NOT make
real network calls. The _execute_submit / _execute_cancel / _execute_replace /
_execute_get_update methods are seam points for future HTTP/WS integration.

No live applied testing. Seam only.
"""
from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.adapter_submit_response import AdapterSubmitResponse
from app.domain.live.adapter_cancel_request import AdapterCancelRequest
from app.domain.live.adapter_cancel_response import AdapterCancelResponse
from app.domain.live.adapter_replace_request import AdapterReplaceRequest
from app.domain.live.adapter_replace_response import AdapterReplaceResponse
from app.domain.live.adapter_order_update import AdapterOrderUpdate
from app.domain.live.external_response_payload import ExternalResponsePayload
from app.domain.live.live_exchange_client import LiveExchangeClient
from app.domain.live.production_request_mapper import ProductionRequestMapper
from app.domain.live.production_response_mapper import ProductionResponseMapper


class ProductionExchangeClient(LiveExchangeClient):
    """Concrete production exchange client.

    Maps internal adapter contracts → external payloads → back to adapter responses.
    Network seam points (_execute_*) are not yet connected to real exchange.
    """

    def __init__(self) -> None:
        self._request_mapper = ProductionRequestMapper()
        self._response_mapper = ProductionResponseMapper()

    # ------------------------------------------------------------------
    # Public adapter interface (LiveExchangeClient)
    # ------------------------------------------------------------------

    def submit_order(self, request: AdapterSubmitRequest) -> AdapterSubmitResponse:
        payload = self._request_mapper.map_submit_request(request)
        raw_response = self._execute_submit(payload)
        return self._response_mapper.map_submit_response(raw_response, request.order_id)

    def cancel_order(self, request: AdapterCancelRequest) -> AdapterCancelResponse:
        payload = self._request_mapper.map_cancel_request(request)
        raw_response = self._execute_cancel(payload)
        return self._response_mapper.map_cancel_response(raw_response, request.order_id)

    def replace_order(self, request: AdapterReplaceRequest) -> AdapterReplaceResponse:
        payload = self._request_mapper.map_replace_request(request)
        raw_response = self._execute_replace(payload)
        return self._response_mapper.map_replace_response(raw_response, request.order_id)

    def get_order_update(self, order_id: str) -> AdapterOrderUpdate:
        raw_response = self._execute_get_update(order_id)
        return self._response_mapper.map_order_update(raw_response, order_id)

    # ------------------------------------------------------------------
    # Seam points — future HTTP/WS integration
    # ------------------------------------------------------------------

    def _execute_submit(self, payload) -> ExternalResponsePayload:
        """Seam: send submit payload to exchange and receive raw response.
        Not yet connected to real exchange. Returns mapped_status='submitted'.
        """
        return ExternalResponsePayload(
            mapped_order_id=payload.order_id,
            mapped_client_order_id=payload.client_order_id,
            mapped_status="submitted",
        )

    def _execute_cancel(self, payload) -> ExternalResponsePayload:
        """Seam: send cancel payload to exchange and receive raw response.
        Not yet connected to real exchange. Returns mapped_status='cancelled'.
        """
        return ExternalResponsePayload(
            mapped_order_id=payload.order_id,
            mapped_client_order_id=payload.client_order_id,
            mapped_status="cancelled",
        )

    def _execute_replace(self, payload) -> ExternalResponsePayload:
        """Seam: send replace payload to exchange and receive raw response.
        Not yet connected to real exchange. Returns mapped_status='replaced'.
        """
        return ExternalResponsePayload(
            mapped_order_id=payload.order_id,
            mapped_client_order_id=payload.client_order_id,
            mapped_status="replaced",
        )

    def _execute_get_update(self, order_id: str) -> ExternalResponsePayload:
        """Seam: fetch order update from exchange.
        Not yet connected to real exchange. Returns mapped_status='no_update'.
        """
        return ExternalResponsePayload(
            mapped_order_id=order_id,
            mapped_status="no_update",
        )
