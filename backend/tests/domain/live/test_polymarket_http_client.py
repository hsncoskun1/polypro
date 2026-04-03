"""Tests for PolymarketHttpClient — v1.0.0 / v1.0.1."""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.domain.live.external_cancel_payload import ExternalCancelPayload
from app.domain.live.external_replace_payload import ExternalReplacePayload
from app.domain.live.external_submit_payload import ExternalSubmitPayload
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.polymarket_http_client import PolymarketHttpClient
from app.domain.live.polymarket_request_signer import PolymarketRequestSigner, PolymarketAuthError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _creds(wallet: str = "0xABC") -> LiveCredentials:
    return LiveCredentials(
        wallet_address=wallet,
        api_key="key_001",
        api_secret="secret_001",
    )


def _empty_creds() -> LiveCredentials:
    return LiveCredentials()


def _submit_payload() -> ExternalSubmitPayload:
    return ExternalSubmitPayload(
        order_id="ord_001",
        market_id="mkt_001",
        side="buy",
        size=10.0,
        limit_price=0.75,
        client_order_id="evt_001",
    )


def _cancel_payload() -> ExternalCancelPayload:
    return ExternalCancelPayload(order_id="ord_001", client_order_id="evt_001")


def _replace_payload() -> ExternalReplacePayload:
    return ExternalReplacePayload(
        order_id="ord_001",
        new_limit_price=0.80,
        new_size=15.0,
        client_order_id="evt_001",
    )


def _mock_signer() -> PolymarketRequestSigner:
    """Returns a signer with fixed timestamp for deterministic test headers."""
    signer = MagicMock(spec=PolymarketRequestSigner)
    signer.build_auth_headers.return_value = {
        "Content-Type": "application/json",
        "POLY_ADDRESS": "0xABC",
        "POLY_SIGNATURE": "test_sig_abc123",
        "POLY_TIMESTAMP": "1700000000",
        "POLY_NONCE": "0",
        "POLY_CREDENTIALS": "eyJ0ZXN0IjoidHJ1ZSJ9",
    }
    return signer


def _client_with_mock_signer() -> PolymarketHttpClient:
    return PolymarketHttpClient(signer=_mock_signer())


def _mock_response(status_code: int, json_body: dict | None = None, text: str = "") -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.text = text
    resp.json.return_value = json_body or {}
    return resp


# ---------------------------------------------------------------------------
# Credentials check (fail-closed) — signer raises PolymarketAuthError
# ---------------------------------------------------------------------------

class TestCredentialsMissing:
    def _failing_signer(self) -> PolymarketRequestSigner:
        signer = MagicMock(spec=PolymarketRequestSigner)
        signer.build_auth_headers.side_effect = PolymarketAuthError("credentials_not_configured")
        return signer

    def test_submit_no_credentials_terminal_failure(self):
        client = PolymarketHttpClient(signer=self._failing_signer())
        result = client.execute_submit(_submit_payload(), _empty_creds())
        assert result.terminal_failure is True
        assert result.mapped_status == ""
        assert "credentials_not_configured" in result.mapped_reject_reason

    def test_cancel_no_credentials_terminal_failure(self):
        client = PolymarketHttpClient(signer=self._failing_signer())
        result = client.execute_cancel(_cancel_payload(), _empty_creds())
        assert result.terminal_failure is True
        assert "credentials_not_configured" in result.mapped_reject_reason

    def test_replace_no_credentials_terminal_failure(self):
        client = PolymarketHttpClient(signer=self._failing_signer())
        result = client.execute_replace(_replace_payload(), _empty_creds())
        assert result.terminal_failure is True
        assert "credentials_not_configured" in result.mapped_reject_reason

    def test_get_update_no_credentials_terminal_failure(self):
        client = PolymarketHttpClient(signer=self._failing_signer())
        result = client.execute_get_update("ord_001", _empty_creds())
        assert result.terminal_failure is True
        assert "credentials_not_configured" in result.mapped_reject_reason

    def test_no_fake_success_on_missing_credentials(self):
        """Missing credentials must never produce mapped_status='submitted'."""
        client = PolymarketHttpClient(signer=self._failing_signer())
        result = client.execute_submit(_submit_payload(), _empty_creds())
        assert result.mapped_status != "submitted"
        assert result.mapped_status != "accepted"


# ---------------------------------------------------------------------------
# Submit — HTTP success path
# ---------------------------------------------------------------------------

class TestSubmitSuccess:
    def test_200_with_order_id_in_response(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"orderID": "exch_ord_999"})
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.mapped_status == "submitted"
        assert result.mapped_order_id == "exch_ord_999"
        assert result.terminal_failure is False

    def test_200_falls_back_to_payload_order_id_if_missing(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {})
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.mapped_status == "submitted"
        assert result.mapped_order_id == "ord_001"

    def test_200_client_order_id_carried(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"orderID": "exch_ord_001"})
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.mapped_client_order_id == "evt_001"

    def test_submit_sends_correct_endpoint(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"orderID": "e001"})
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            client.execute_submit(_submit_payload(), _creds())
        call_url = mock_post.call_args[0][0]
        assert "polymarket.com" in call_url
        assert "/order" in call_url

    def test_submit_body_contains_market_id(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"orderID": "e001"})
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            client.execute_submit(_submit_payload(), _creds())
        body = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert body["market_id"] == "mkt_001"
        assert body["side"] == "buy"

    def test_submit_headers_contain_poly_signature(self):
        """Signed headers are forwarded to httpx.post (v1.0.1 integration)."""
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"orderID": "e001"})
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            client.execute_submit(_submit_payload(), _creds())
        headers = mock_post.call_args.kwargs.get("headers") or mock_post.call_args[1].get("headers")
        assert headers["POLY_SIGNATURE"] == "test_sig_abc123"
        assert headers["POLY_ADDRESS"] == "0xABC"


# ---------------------------------------------------------------------------
# Cancel — HTTP success path
# ---------------------------------------------------------------------------

class TestCancelSuccess:
    def test_200_returns_cancelled(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {})
        with patch("httpx.delete", return_value=mock_resp):
            result = client.execute_cancel(_cancel_payload(), _creds())
        assert result.mapped_status == "cancelled"
        assert result.mapped_order_id == "ord_001"
        assert result.terminal_failure is False

    def test_cancel_sends_correct_endpoint(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {})
        with patch("httpx.delete", return_value=mock_resp) as mock_del:
            client.execute_cancel(_cancel_payload(), _creds())
        call_url = mock_del.call_args[0][0]
        assert "polymarket.com" in call_url

    def test_cancel_body_contains_order_id(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {})
        with patch("httpx.delete", return_value=mock_resp) as mock_del:
            client.execute_cancel(_cancel_payload(), _creds())
        body = mock_del.call_args.kwargs.get("json") or mock_del.call_args[1].get("json")
        assert "ord_001" in body["orderIDs"]


# ---------------------------------------------------------------------------
# Replace — HTTP success path
# ---------------------------------------------------------------------------

class TestReplaceSuccess:
    def test_200_returns_replaced(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"orderID": "new_ord_002"})
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_replace(_replace_payload(), _creds())
        assert result.mapped_status == "replaced"
        assert result.mapped_order_id == "new_ord_002"
        assert result.terminal_failure is False

    def test_replace_body_contains_new_price(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"orderID": "new_002"})
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            client.execute_replace(_replace_payload(), _creds())
        body = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert body["new_limit_price"] == 0.80
        assert body["new_size"] == 15.0


# ---------------------------------------------------------------------------
# Get update — HTTP success path
# ---------------------------------------------------------------------------

class TestGetUpdateSuccess:
    def test_200_live_status_maps_to_update_received(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"status": "LIVE", "size_matched": "5.0", "size_remaining": "5.0"})
        with patch("httpx.get", return_value=mock_resp):
            result = client.execute_get_update("ord_001", _creds())
        assert result.mapped_status == "update_received"
        assert result.filled_size == 5.0
        assert result.remaining_size == 5.0

    def test_200_cancelled_status_maps_to_cancelled(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"status": "CANCELLED"})
        with patch("httpx.get", return_value=mock_resp):
            result = client.execute_get_update("ord_001", _creds())
        assert result.mapped_status == "cancelled"

    def test_200_unknown_status_maps_to_no_update(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"status": "WEIRD_STATUS"})
        with patch("httpx.get", return_value=mock_resp):
            result = client.execute_get_update("ord_001", _creds())
        assert result.mapped_status == "no_update"

    def test_404_returns_no_update(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(404)
        with patch("httpx.get", return_value=mock_resp):
            result = client.execute_get_update("ord_001", _creds())
        assert result.mapped_status == "no_update"
        assert result.terminal_failure is False

    def test_get_update_url_contains_order_id(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(200, {"status": "LIVE"})
        with patch("httpx.get", return_value=mock_resp) as mock_get:
            client.execute_get_update("ord_999", _creds())
        call_url = mock_get.call_args[0][0]
        assert "ord_999" in call_url


# ---------------------------------------------------------------------------
# HTTP error mapping
# ---------------------------------------------------------------------------

class TestHttpErrorMapping:
    def test_400_submit_terminal_failure(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(400, text="bad request")
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.terminal_failure is True
        assert result.mapped_status == "rejected"

    def test_422_terminal_failure(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(422, text="unprocessable")
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.terminal_failure is True

    def test_401_auth_error_terminal_failure(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(401)
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.terminal_failure is True
        assert "auth_error" in result.mapped_reject_reason

    def test_429_rate_limited_retryable(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(429)
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.retryable is True
        assert result.terminal_failure is False

    def test_500_server_error_retryable(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(500)
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.retryable is True
        assert result.terminal_failure is False

    def test_503_retryable(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(503)
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.retryable is True
        assert result.terminal_failure is False

    def test_unknown_status_fail_closed(self):
        client = _client_with_mock_signer()
        mock_resp = _mock_response(418)  # I'm a teapot — unknown
        with patch("httpx.post", return_value=mock_resp):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.terminal_failure is True
        assert result.retryable is False


# ---------------------------------------------------------------------------
# Timeout and exception handling
# ---------------------------------------------------------------------------

class TestTimeoutAndExceptions:
    def test_submit_timeout_retryable(self):
        client = _client_with_mock_signer()
        with patch("httpx.post", side_effect=httpx.TimeoutException("timeout")):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.retryable is True
        assert result.terminal_failure is False
        assert result.mapped_status == ""

    def test_cancel_timeout_retryable(self):
        client = _client_with_mock_signer()
        with patch("httpx.delete", side_effect=httpx.TimeoutException("timeout")):
            result = client.execute_cancel(_cancel_payload(), _creds())
        assert result.retryable is True
        assert result.terminal_failure is False

    def test_replace_timeout_retryable(self):
        client = _client_with_mock_signer()
        with patch("httpx.post", side_effect=httpx.TimeoutException("timeout")):
            result = client.execute_replace(_replace_payload(), _creds())
        assert result.retryable is True

    def test_get_update_timeout_retryable(self):
        client = _client_with_mock_signer()
        with patch("httpx.get", side_effect=httpx.TimeoutException("timeout")):
            result = client.execute_get_update("ord_001", _creds())
        assert result.retryable is True

    def test_submit_unexpected_exception_terminal(self):
        client = _client_with_mock_signer()
        with patch("httpx.post", side_effect=RuntimeError("unexpected")):
            result = client.execute_submit(_submit_payload(), _creds())
        assert result.terminal_failure is True
        assert result.retryable is False


# ---------------------------------------------------------------------------
# Auth-signing integration (v1.0.1)
# ---------------------------------------------------------------------------

class TestAuthSigningIntegration:
    def test_signer_called_for_submit(self):
        """Signer is invoked with correct method and path for submit."""
        mock_sig = _mock_signer()
        client = PolymarketHttpClient(signer=mock_sig)
        mock_resp = _mock_response(200, {"orderID": "e001"})
        with patch("httpx.post", return_value=mock_resp):
            client.execute_submit(_submit_payload(), _creds())
        mock_sig.build_auth_headers.assert_called_once()
        call_args = mock_sig.build_auth_headers.call_args
        assert call_args[0][1] == "POST"    # method
        assert call_args[0][2] == "/order"  # path

    def test_signer_called_for_cancel(self):
        mock_sig = _mock_signer()
        client = PolymarketHttpClient(signer=mock_sig)
        mock_resp = _mock_response(200, {})
        with patch("httpx.delete", return_value=mock_resp):
            client.execute_cancel(_cancel_payload(), _creds())
        call_args = mock_sig.build_auth_headers.call_args
        assert call_args[0][1] == "DELETE"

    def test_signer_called_for_get_update_with_order_id_in_path(self):
        mock_sig = _mock_signer()
        client = PolymarketHttpClient(signer=mock_sig)
        mock_resp = _mock_response(200, {"status": "LIVE"})
        with patch("httpx.get", return_value=mock_resp):
            client.execute_get_update("ord_999", _creds())
        call_args = mock_sig.build_auth_headers.call_args
        assert call_args[0][1] == "GET"
        assert "ord_999" in call_args[0][2]  # path contains order_id

    def test_missing_api_key_fails_closed_not_fake_success(self):
        """Signer raises PolymarketAuthError when api_key missing → terminal_failure."""
        real_signer = PolymarketRequestSigner()
        client = PolymarketHttpClient(signer=real_signer)
        no_key_creds = LiveCredentials(wallet_address="0xABC", api_secret="secret")
        result = client.execute_submit(_submit_payload(), no_key_creds)
        assert result.terminal_failure is True
        assert result.mapped_status != "submitted"

    def test_missing_api_secret_fails_closed(self):
        real_signer = PolymarketRequestSigner()
        client = PolymarketHttpClient(signer=real_signer)
        no_secret_creds = LiveCredentials(wallet_address="0xABC", api_key="key")
        result = client.execute_submit(_submit_payload(), no_secret_creds)
        assert result.terminal_failure is True
        assert result.mapped_status != "submitted"

    def test_missing_wallet_address_fails_closed(self):
        real_signer = PolymarketRequestSigner()
        client = PolymarketHttpClient(signer=real_signer)
        no_wallet = LiveCredentials(api_key="key", api_secret="secret")
        result = client.execute_submit(_submit_payload(), no_wallet)
        assert result.terminal_failure is True
