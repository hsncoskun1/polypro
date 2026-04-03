"""Polymarket HTTP client — v1.0.0 / v1.0.1.

Concrete HTTP client for Polymarket CLOB REST API.
Replaces seam _execute_* points in ProductionExchangeClient with real network calls.

v1.0.1: Integrated PolymarketRequestSigner — all requests carry full POLY_* auth headers.

Endpoints:
  POST   https://clob.polymarket.com/order           — submit
  DELETE https://clob.polymarket.com/order           — cancel (body: {orderIDs: [id]})
  POST   https://clob.polymarket.com/order           — replace (cancel+resubmit flow)
  GET    https://clob.polymarket.com/order/{id}      — get order update

Auth: Polymarket CLOB Level 2 auth via PolymarketRequestSigner.
  - Missing credentials → terminal_failure=True (fail-closed, no network call).
  - PolymarketAuthError from signer → terminal_failure=True.

No live applied testing. Do not call from simulation paths.
"""
import json

import httpx

from app.domain.live.external_submit_payload import ExternalSubmitPayload
from app.domain.live.external_cancel_payload import ExternalCancelPayload
from app.domain.live.external_replace_payload import ExternalReplacePayload
from app.domain.live.external_response_payload import ExternalResponsePayload
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.client_timeout_policy import ClientTimeoutPolicy
from app.domain.live.polymarket_request_signer import PolymarketRequestSigner, PolymarketAuthError

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
    All requests signed via PolymarketRequestSigner (v1.0.1).
    Credentials required — fails closed when not configured.
    """

    def __init__(
        self,
        timeout_policy: ClientTimeoutPolicy | None = None,
        signer: PolymarketRequestSigner | None = None,
    ) -> None:
        self._timeout = (timeout_policy or ClientTimeoutPolicy()).timeout_seconds
        self._signer = signer or PolymarketRequestSigner()

    # ------------------------------------------------------------------
    # Public execute methods
    # ------------------------------------------------------------------

    def execute_submit(
        self,
        payload: ExternalSubmitPayload,
        credentials: LiveCredentials,
    ) -> ExternalResponsePayload:
        """Submit a new order to Polymarket CLOB. Fail-closed if credentials missing."""
        body = self._build_submit_body(payload)
        body_str = json.dumps(body, separators=(",", ":"))
        try:
            headers = self._signer.build_auth_headers(credentials, "POST", "/order", body_str)
        except PolymarketAuthError:
            return self._credentials_missing_response()
        try:
            response = httpx.post(_ORDER_URL, json=body, headers=headers, timeout=self._timeout)
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
        body = {"orderIDs": [payload.order_id]}
        body_str = json.dumps(body, separators=(",", ":"))
        try:
            headers = self._signer.build_auth_headers(credentials, "DELETE", "/order", body_str)
        except PolymarketAuthError:
            return self._credentials_missing_response()
        try:
            response = httpx.delete(_ORDER_URL, json=body, headers=headers, timeout=self._timeout)
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
        body = self._build_replace_body(payload)
        body_str = json.dumps(body, separators=(",", ":"))
        try:
            headers = self._signer.build_auth_headers(credentials, "POST", "/order", body_str)
        except PolymarketAuthError:
            return self._credentials_missing_response()
        try:
            response = httpx.post(_ORDER_URL, json=body, headers=headers, timeout=self._timeout)
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
        path = f"/order/{order_id}"
        try:
            headers = self._signer.build_auth_headers(credentials, "GET", path, "")
        except PolymarketAuthError:
            return self._credentials_missing_response()
        try:
            url = _ORDER_BY_ID_URL.format(order_id=order_id)
            response = httpx.get(url, headers=headers, timeout=self._timeout)
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
