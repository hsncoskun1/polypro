"""Polymarket HTTP client — v1.0.0.

Concrete HTTP client for Polymarket CLOB REST API.
Replaces seam _execute_* points in ProductionExchangeClient with real network calls.

Endpoints:
  POST   https://clob.polymarket.com/order           — submit
  DELETE https://clob.polymarket.com/order           — cancel (body: {orderIDs: [id]})
  POST   https://clob.polymarket.com/order           — replace (cancel+resubmit flow)
  GET    https://clob.polymarket.com/order/{id}      — get order update

Auth: Polymarket CLOB requires POLY_ADDRESS + POLY_SIGNATURE headers.
  - POLY_SIGNATURE signing is v1.0.1 scope.
  - Requests without wallet_address fail-closed (terminal_failure=True).
  - Requests with wallet_address but no signature will be rejected by exchange (401).

No live applied testing. Do not call from simulation paths.
"""
import httpx

from app.domain.live.external_submit_payload import ExternalSubmitPayload
from app.domain.live.external_cancel_payload import ExternalCancelPayload
from app.domain.live.external_replace_payload import ExternalReplacePayload
from app.domain.live.external_response_payload import ExternalResponsePayload
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.client_timeout_policy import ClientTimeoutPolicy

_CLOB_BASE = "https://clob.polymarket.com"
_ORDER_URL = f"{_CLOB_BASE}/order"
_ORDER_BY_ID_URL = f"{_CLOB_BASE}/order/{{order_id}}"

_ORDER_STATUS_MAP: dict[str, str] = {
    "LIVE": "update_received",
    "MATCHED": "update_received",
    "DELAYED": "update_received",
    "CANCELLED": "cancelled",
    "UNMATCHED": "no_update",
}


class PolymarketHttpClient:
    """Concrete HTTP client for Polymarket CLOB REST API.

    Handles submit, cancel, replace, and order update HTTP operations.
    Credentials required — fails closed when not configured.
    POLY_SIGNATURE signing to be injected in v1.0.1.
    """

    def __init__(
        self,
        timeout_policy: ClientTimeoutPolicy | None = None,
    ) -> None:
        self._timeout = (timeout_policy or ClientTimeoutPolicy()).timeout_seconds

    # ------------------------------------------------------------------
    # Public execute methods
    # ------------------------------------------------------------------

    def execute_submit(
        self,
        payload: ExternalSubmitPayload,
        credentials: LiveCredentials,
    ) -> ExternalResponsePayload:
        """Submit a new order to Polymarket CLOB. Fail-closed if credentials missing."""
        if not self._credentials_present(credentials):
            return self._credentials_missing_response()
        try:
            response = httpx.post(
                _ORDER_URL,
                json=self._build_submit_body(payload),
                headers=self._build_headers(credentials),
                timeout=self._timeout,
            )
            return self._parse_submit_response(response, payload)
        except httpx.TimeoutException:
            return self._timeout_response()
        except Exception:
            return self._unknown_error_response()

    def execute_cancel(
        self,
        payload: ExternalCancelPayload,
        credentials: LiveCredentials,
    ) -> ExternalResponsePayload:
        """Cancel an existing order on Polymarket CLOB. Fail-closed if credentials missing."""
        if not self._credentials_present(credentials):
            return self._credentials_missing_response()
        try:
            response = httpx.delete(
                _ORDER_URL,
                json={"orderIDs": [payload.order_id]},
                headers=self._build_headers(credentials),
                timeout=self._timeout,
            )
            return self._parse_cancel_response(response, payload)
        except httpx.TimeoutException:
            return self._timeout_response()
        except Exception:
            return self._unknown_error_response()

    def execute_replace(
        self,
        payload: ExternalReplacePayload,
        credentials: LiveCredentials,
    ) -> ExternalResponsePayload:
        """Replace (amend) an order on Polymarket CLOB. Fail-closed if credentials missing."""
        if not self._credentials_present(credentials):
            return self._credentials_missing_response()
        try:
            response = httpx.post(
                _ORDER_URL,
                json=self._build_replace_body(payload),
                headers=self._build_headers(credentials),
                timeout=self._timeout,
            )
            return self._parse_replace_response(response, payload)
        except httpx.TimeoutException:
            return self._timeout_response()
        except Exception:
            return self._unknown_error_response()

    def execute_get_update(
        self,
        order_id: str,
        credentials: LiveCredentials,
    ) -> ExternalResponsePayload:
        """Fetch latest order status from Polymarket CLOB. Fail-closed if credentials missing."""
        if not self._credentials_present(credentials):
            return self._credentials_missing_response()
        try:
            url = _ORDER_BY_ID_URL.format(order_id=order_id)
            response = httpx.get(
                url,
                headers=self._build_headers(credentials),
                timeout=self._timeout,
            )
            return self._parse_update_response(response, order_id)
        except httpx.TimeoutException:
            return self._timeout_response()
        except Exception:
            return self._unknown_error_response()

    # ------------------------------------------------------------------
    # Request builders
    # ------------------------------------------------------------------

    def _build_submit_body(self, payload: ExternalSubmitPayload) -> dict:
        return {
            "order_id": payload.order_id,
            "market_id": payload.market_id,
            "side": payload.side,
            "size": payload.size,
            "limit_price": payload.limit_price,
            "client_order_id": payload.client_order_id,
        }

    def _build_replace_body(self, payload: ExternalReplacePayload) -> dict:
        return {
            "order_id": payload.order_id,
            "new_limit_price": payload.new_limit_price,
            "new_size": payload.new_size,
            "client_order_id": payload.client_order_id,
        }

    def _build_headers(self, credentials: LiveCredentials) -> dict:
        """Build Polymarket CLOB auth headers.

        POLY_SIGNATURE is empty in v1.0.0 — signing not yet implemented.
        Requests will be rejected by exchange until v1.0.1 signing is wired.
        """
        return {
            "Content-Type": "application/json",
            "POLY_ADDRESS": credentials.wallet_address,
            "POLY_SIGNATURE": "",   # v1.0.1: real HMAC/wallet signing
            "POLY_TIMESTAMP": "",
            "POLY_NONCE": "",
        }

    # ------------------------------------------------------------------
    # Response parsers
    # ------------------------------------------------------------------

    def _parse_submit_response(
        self,
        response: httpx.Response,
        payload: ExternalSubmitPayload,
    ) -> ExternalResponsePayload:
        if response.status_code == 200:
            data = self._safe_json(response)
            order_id = data.get("orderID") or data.get("order_id") or payload.order_id
            return ExternalResponsePayload(
                mapped_order_id=order_id,
                mapped_client_order_id=payload.client_order_id,
                mapped_status="submitted",
            )
        return self._map_http_error(response)

    def _parse_cancel_response(
        self,
        response: httpx.Response,
        payload: ExternalCancelPayload,
    ) -> ExternalResponsePayload:
        if response.status_code == 200:
            return ExternalResponsePayload(
                mapped_order_id=payload.order_id,
                mapped_client_order_id=payload.client_order_id,
                mapped_status="cancelled",
            )
        return self._map_http_error(response)

    def _parse_replace_response(
        self,
        response: httpx.Response,
        payload: ExternalReplacePayload,
    ) -> ExternalResponsePayload:
        if response.status_code == 200:
            data = self._safe_json(response)
            new_order_id = data.get("orderID") or data.get("order_id") or payload.order_id
            return ExternalResponsePayload(
                mapped_order_id=new_order_id,
                mapped_client_order_id=payload.client_order_id,
                mapped_status="replaced",
            )
        return self._map_http_error(response)

    def _parse_update_response(
        self,
        response: httpx.Response,
        order_id: str,
    ) -> ExternalResponsePayload:
        if response.status_code == 200:
            data = self._safe_json(response)
            raw_status = data.get("status", "")
            mapped = _ORDER_STATUS_MAP.get(raw_status.upper() if raw_status else "", "no_update")
            return ExternalResponsePayload(
                mapped_order_id=order_id,
                mapped_status=mapped,
                filled_size=float(data.get("size_matched", 0) or 0),
                remaining_size=float(data.get("size_remaining", 0) or 0),
            )
        if response.status_code == 404:
            return ExternalResponsePayload(
                mapped_order_id=order_id,
                mapped_status="no_update",
            )
        return self._map_http_error(response)

    # ------------------------------------------------------------------
    # Error helpers
    # ------------------------------------------------------------------

    def _map_http_error(self, response: httpx.Response) -> ExternalResponsePayload:
        """Map HTTP error codes to ExternalResponsePayload. Fail-closed on unknown."""
        if response.status_code in (400, 422):
            return ExternalResponsePayload(
                mapped_status="rejected",
                mapped_reject_reason=response.text[:200],
                terminal_failure=True,
            )
        if response.status_code == 401:
            return ExternalResponsePayload(
                mapped_status="",
                mapped_reject_reason="auth_error",
                terminal_failure=True,
            )
        if response.status_code == 429:
            return ExternalResponsePayload(
                mapped_status="",
                retryable=True,
                terminal_failure=False,
            )
        if response.status_code in (500, 502, 503, 504):
            return ExternalResponsePayload(
                mapped_status="",
                retryable=True,
                terminal_failure=False,
            )
        # Unknown — fail-closed
        return ExternalResponsePayload(
            mapped_status="",
            mapped_reject_reason=f"unexpected_http_{response.status_code}",
            terminal_failure=True,
        )

    def _credentials_present(self, credentials: LiveCredentials) -> bool:
        """Fail-closed: wallet_address is required for all Polymarket CLOB operations."""
        return bool(credentials.wallet_address)

    def _credentials_missing_response(self) -> ExternalResponsePayload:
        return ExternalResponsePayload(
            mapped_status="",
            mapped_reject_reason="credentials_not_configured",
            terminal_failure=True,
        )

    def _timeout_response(self) -> ExternalResponsePayload:
        return ExternalResponsePayload(
            mapped_status="",
            retryable=True,
            terminal_failure=False,
        )

    def _unknown_error_response(self) -> ExternalResponsePayload:
        return ExternalResponsePayload(
            mapped_status="",
            mapped_reject_reason="unknown_error",
            terminal_failure=True,
        )

    def _safe_json(self, response: httpx.Response) -> dict:
        try:
            return response.json()
        except Exception:
            return {}
