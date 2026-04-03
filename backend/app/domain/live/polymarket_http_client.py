"""Polymarket HTTP client — v1.0.0 / v1.0.1 / v1.0.2.

Concrete HTTP client for Polymarket CLOB REST API.
Replaces seam _execute_* points in ProductionExchangeClient with real network calls.

v1.0.1: Integrated PolymarketRequestSigner — all requests carry full POLY_* auth headers.
v1.0.2: Added execute_get_balance — fetches real exchange balance via CLOB balance-allowance endpoint.

Endpoints:
  POST   https://clob.polymarket.com/order                              — submit
  DELETE https://clob.polymarket.com/order                              — cancel (body: {orderIDs: [id]})
  POST   https://clob.polymarket.com/order                              — replace (cancel+resubmit flow)
  GET    https://clob.polymarket.com/order/{id}                         — get order update
  GET    https://clob.polymarket.com/balance-allowance?asset_type=COLLATERAL — get balance

Auth: Polymarket CLOB Level 2 auth via PolymarketRequestSigner.
  - Missing credentials → terminal_failure=True (fail-closed, no network call).
  - PolymarketAuthError from signer → terminal_failure=True.

No live applied testing. Do not call from simulation paths.
"""
import json
import time

import httpx

from app.domain.live.external_submit_payload import ExternalSubmitPayload
from app.domain.live.external_cancel_payload import ExternalCancelPayload
from app.domain.live.external_replace_payload import ExternalReplacePayload
from app.domain.live.external_response_payload import ExternalResponsePayload
from app.domain.live.balance_fetch_payload import BalanceFetchPayload
from app.domain.live.balance_sync_result import BalanceSyncResult
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.client_timeout_policy import ClientTimeoutPolicy
from app.domain.live.polymarket_request_signer import PolymarketRequestSigner, PolymarketAuthError

_CLOB_BASE = "https://clob.polymarket.com"
_ORDER_URL = f"{_CLOB_BASE}/order"
_ORDER_BY_ID_URL = f"{_CLOB_BASE}/order/{{order_id}}"
_BALANCE_PATH = "/balance-allowance"
_BALANCE_URL = f"{_CLOB_BASE}{_BALANCE_PATH}?asset_type=COLLATERAL"

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

    def execute_get_balance(
        self,
        credentials: LiveCredentials,
        payload: BalanceFetchPayload | None = None,
    ) -> BalanceSyncResult:
        """Fetch real account balance from Polymarket CLOB. Fail-closed if credentials missing.

        Endpoint: GET https://clob.polymarket.com/balance-allowance?asset_type=COLLATERAL

        Returns:
            BalanceSyncResult with sync_success=True and balance fields populated on success.
            On any failure: sync_success=False, terminal_failure or retryable set accordingly.
        """
        payload = payload or BalanceFetchPayload()
        try:
            headers = self._signer.build_auth_headers(credentials, "GET", _BALANCE_PATH, "")
        except PolymarketAuthError:
            return self._balance_credentials_missing_result()
        try:
            response = httpx.get(_BALANCE_URL, headers=headers, timeout=self._timeout)
            return self._parse_balance_response(response, payload)
        except httpx.TimeoutException:
            return self._balance_timeout_result()
        except Exception:
            return self._balance_unknown_error_result()

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

    def _parse_balance_response(
        self,
        response: httpx.Response,
        payload: BalanceFetchPayload,
    ) -> BalanceSyncResult:
        """Parse exchange balance response into BalanceSyncResult. Fail-closed on any anomaly."""
        synced_at = str(int(time.time()))

        if response.status_code == 200:
            raw = self._safe_json(response)
            raw_balance_str = raw.get("balance")
            if raw_balance_str is None:
                return BalanceSyncResult(
                    sync_success=False,
                    terminal_failure=True,
                    reject_reason="balance_field_missing",
                    raw_balance_payload=raw,
                    synced_at=synced_at,
                )
            try:
                balance_value = float(raw_balance_str)
            except (TypeError, ValueError):
                return BalanceSyncResult(
                    sync_success=False,
                    terminal_failure=True,
                    reject_reason="balance_field_malformed",
                    raw_balance_payload=raw,
                    synced_at=synced_at,
                )
            currency = payload.currency
            return BalanceSyncResult(
                total_balance=balance_value,
                available_balance=balance_value,
                current_balance=balance_value,
                currency=currency,
                synced_at=synced_at,
                sync_success=True,
                retryable=False,
                terminal_failure=False,
                raw_balance_payload=raw,
                normalized_balance_result=(
                    f"balance={balance_value} {currency} synced_at={synced_at}"
                ),
            )

        if response.status_code == 401:
            return BalanceSyncResult(
                sync_success=False,
                terminal_failure=True,
                reject_reason="auth_error",
                synced_at=synced_at,
            )
        if response.status_code == 429:
            return BalanceSyncResult(
                sync_success=False,
                retryable=True,
                terminal_failure=False,
                reject_reason="rate_limited",
                synced_at=synced_at,
            )
        if response.status_code in (400, 422):
            return BalanceSyncResult(
                sync_success=False,
                terminal_failure=True,
                reject_reason=f"rejected_{response.status_code}",
                synced_at=synced_at,
            )
        if response.status_code in (500, 502, 503, 504):
            return BalanceSyncResult(
                sync_success=False,
                retryable=True,
                terminal_failure=False,
                reject_reason=f"server_error_{response.status_code}",
                synced_at=synced_at,
            )
        # Unknown — fail-closed
        return BalanceSyncResult(
            sync_success=False,
            terminal_failure=True,
            reject_reason=f"unexpected_http_{response.status_code}",
            synced_at=synced_at,
        )

    def _balance_credentials_missing_result(self) -> BalanceSyncResult:
        return BalanceSyncResult(
            sync_success=False,
            terminal_failure=True,
            reject_reason="credentials_not_configured",
        )

    def _balance_timeout_result(self) -> BalanceSyncResult:
        return BalanceSyncResult(
            sync_success=False,
            retryable=True,
            terminal_failure=False,
            reject_reason="timeout",
        )

    def _balance_unknown_error_result(self) -> BalanceSyncResult:
        return BalanceSyncResult(
            sync_success=False,
            terminal_failure=True,
            reject_reason="unknown_error",
        )

    def _safe_json(self, response: httpx.Response) -> dict:
        try:
            return response.json()
        except Exception:
            return {}
