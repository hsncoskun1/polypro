"""Production exchange client — concrete implementation — v0.8.0 / v1.0.0.

Concrete implementation of LiveExchangeClient for production use.
Maps internal adapter contracts to external payloads via PolymarketHttpClient.

v1.0.0: _execute_* methods wired to PolymarketHttpClient (real HTTP calls).
Credentials required — fails closed when not configured.
POLY_SIGNATURE signing not yet implemented (v1.0.1 scope).

No live applied testing. Production use only.
"""
from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.adapter_submit_response import AdapterSubmitResponse
from app.domain.live.adapter_cancel_request import AdapterCancelRequest
from app.domain.live.adapter_cancel_response import AdapterCancelResponse
from app.domain.live.adapter_replace_request import AdapterReplaceRequest
from app.domain.live.adapter_replace_response import AdapterReplaceResponse
from app.domain.live.adapter_order_update import AdapterOrderUpdate
from app.domain.live.external_response_payload import ExternalResponsePayload
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.live_exchange_client import LiveExchangeClient
from app.domain.live.polymarket_http_client import PolymarketHttpClient
from app.domain.live.production_request_mapper import ProductionRequestMapper
from app.domain.live.production_response_mapper import ProductionResponseMapper


class ProductionExchangeClient(LiveExchangeClient):
    """Concrete production exchange client.

    Maps internal adapter contracts → external payloads → PolymarketHttpClient → adapter responses.
    HTTP client and credentials are injectable for testing.
    """

    def __init__(
        self,
        http_client: PolymarketHttpClient | None = None,
        credentials: LiveCredentials | None = None,
    ) -> None:
        self._request_mapper = ProductionRequestMapper()
        self._response_mapper = ProductionResponseMapper()
        self._http_client = http_client or PolymarketHttpClient()
        self._credentials = credentials or LiveCredentials()

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
    # HTTP execution — delegates to PolymarketHttpClient
    # ------------------------------------------------------------------

    def _execute_submit(self, payload) -> ExternalResponsePayload:
        return self._http_client.execute_submit(payload, self._credentials)

    def _execute_cancel(self, payload) -> ExternalResponsePayload:
        return self._http_client.execute_cancel(payload, self._credentials)

    def _execute_replace(self, payload) -> ExternalResponsePayload:
        return self._http_client.execute_replace(payload, self._credentials)

    def _execute_get_update(self, order_id: str) -> ExternalResponsePayload:
        return self._http_client.execute_get_update(order_id, self._credentials)
