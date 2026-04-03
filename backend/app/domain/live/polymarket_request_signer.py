"""Polymarket CLOB request signer — v1.0.1.

Computes Polymarket Level 2 auth headers for CLOB REST API requests.

Auth header set:
  POLY_ADDRESS     — funder_address (or wallet_address as fallback)
  POLY_SIGNATURE   — HMAC-SHA256(timestamp + METHOD + path + body, api_secret)
  POLY_TIMESTAMP   — Unix timestamp in seconds (str)
  POLY_NONCE       — request nonce (default "0")
  POLY_CREDENTIALS — base64(json({key, secret, passphrase}))

Signing algorithm:
  message   = timestamp + method.upper() + request_path + body
  signature = HMAC-SHA256(message, api_secret).hexdigest()

Fail-closed:
  Missing api_key / api_secret / wallet_address → raises PolymarketAuthError.
  Caller (PolymarketHttpClient) converts this to terminal_failure=True.

No live testing. No network calls. Pure cryptographic helper.
"""
import base64
import hashlib
import hmac
import json
import time

from app.domain.live.live_credentials import LiveCredentials


class PolymarketAuthError(Exception):
    """Raised when credentials are insufficient to produce a valid signature."""


class PolymarketRequestSigner:
    """Builds Polymarket CLOB Level 2 auth headers.

    Injectable timestamp provider for deterministic testing.
    """

    def __init__(self, timestamp_provider=None) -> None:
        """
        Args:
            timestamp_provider: callable () -> str — returns Unix timestamp as string.
                                 Defaults to real time.time(). Inject for tests.
        """
        self._timestamp_provider = timestamp_provider or self._default_timestamp

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_auth_headers(
        self,
        credentials: LiveCredentials,
        method: str,
        request_path: str,
        body: str = "",
        nonce: str = "0",
    ) -> dict:
        """Build full Polymarket CLOB auth header dict.

        Args:
            credentials: LiveCredentials with api_key, api_secret, wallet_address.
            method:       HTTP method (GET, POST, DELETE).
            request_path: URL path component (e.g. "/order", "/order/ord_001").
            body:         Request body as JSON string (empty string if no body).
            nonce:        Request nonce, default "0".

        Returns:
            dict with Content-Type + POLY_* headers.

        Raises:
            PolymarketAuthError: if required credentials missing.
        """
        self._assert_credentials_ready(credentials)
        timestamp = self._timestamp_provider()
        signature = self._compute_hmac(timestamp, method.upper(), request_path, body, credentials.api_secret)
        encoded_creds = self._encode_credentials(credentials)
        address = credentials.funder_address or credentials.wallet_address

        return {
            "Content-Type": "application/json",
            "POLY_ADDRESS": address,
            "POLY_SIGNATURE": signature,
            "POLY_TIMESTAMP": timestamp,
            "POLY_NONCE": nonce,
            "POLY_CREDENTIALS": encoded_creds,
        }

    def compute_signature(
        self,
        timestamp: str,
        method: str,
        request_path: str,
        body: str,
        api_secret: str,
    ) -> str:
        """Compute HMAC-SHA256 signature directly. Exposed for testing."""
        return self._compute_hmac(timestamp, method.upper(), request_path, body, api_secret)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_hmac(
        self,
        timestamp: str,
        method: str,
        request_path: str,
        body: str,
        secret: str,
    ) -> str:
        message = timestamp + method + request_path + body
        return hmac.new(
            key=secret.encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def _encode_credentials(self, credentials: LiveCredentials) -> str:
        obj = {
            "key": credentials.api_key,
            "secret": credentials.api_secret,
            "passphrase": credentials.api_passphrase,
        }
        return base64.b64encode(json.dumps(obj, separators=(",", ":")).encode("utf-8")).decode("utf-8")

    def _assert_credentials_ready(self, credentials: LiveCredentials) -> None:
        missing = []
        if not credentials.api_key:
            missing.append("api_key")
        if not credentials.api_secret:
            missing.append("api_secret")
        if not credentials.wallet_address:
            missing.append("wallet_address")
        if missing:
            raise PolymarketAuthError(
                f"Cannot sign request — missing credentials: {', '.join(missing)}"
            )

    @staticmethod
    def _default_timestamp() -> str:
        return str(int(time.time()))
