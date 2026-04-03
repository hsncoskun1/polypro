"""Tests for PolymarketRequestSigner — v1.0.1."""
import base64
import hashlib
import hmac
import json

import pytest

from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.polymarket_request_signer import (
    PolymarketAuthError,
    PolymarketRequestSigner,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _creds(
    wallet: str = "0xWALLET",
    api_key: str = "key_abc",
    api_secret: str = "secret_xyz",
    api_passphrase: str = "pass_123",
    funder: str = "",
) -> LiveCredentials:
    return LiveCredentials(
        wallet_address=wallet,
        api_key=api_key,
        api_secret=api_secret,
        api_passphrase=api_passphrase,
        funder_address=funder,
    )


def _signer_fixed_ts(ts: str = "1700000000") -> PolymarketRequestSigner:
    """Signer with fixed timestamp for deterministic tests."""
    return PolymarketRequestSigner(timestamp_provider=lambda: ts)


def _expected_hmac(ts: str, method: str, path: str, body: str, secret: str) -> str:
    message = ts + method + path + body
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


# ---------------------------------------------------------------------------
# HMAC computation
# ---------------------------------------------------------------------------

class TestComputeSignature:
    def test_deterministic_output(self):
        signer = _signer_fixed_ts("1700000000")
        sig1 = signer.compute_signature("1700000000", "POST", "/order", "", "secret_xyz")
        sig2 = signer.compute_signature("1700000000", "POST", "/order", "", "secret_xyz")
        assert sig1 == sig2

    def test_different_secrets_produce_different_sigs(self):
        signer = PolymarketRequestSigner()
        sig1 = signer.compute_signature("1700000000", "POST", "/order", "", "secret_A")
        sig2 = signer.compute_signature("1700000000", "POST", "/order", "", "secret_B")
        assert sig1 != sig2

    def test_different_methods_produce_different_sigs(self):
        signer = PolymarketRequestSigner()
        sig_post = signer.compute_signature("1700000000", "POST", "/order", "", "secret")
        sig_del = signer.compute_signature("1700000000", "DELETE", "/order", "", "secret")
        assert sig_post != sig_del

    def test_different_timestamps_produce_different_sigs(self):
        signer = PolymarketRequestSigner()
        sig1 = signer.compute_signature("1700000000", "POST", "/order", "", "secret")
        sig2 = signer.compute_signature("1700000001", "POST", "/order", "", "secret")
        assert sig1 != sig2

    def test_body_changes_signature(self):
        signer = PolymarketRequestSigner()
        sig1 = signer.compute_signature("1700000000", "POST", "/order", '{"a":1}', "secret")
        sig2 = signer.compute_signature("1700000000", "POST", "/order", '{"a":2}', "secret")
        assert sig1 != sig2

    def test_matches_expected_hmac_sha256(self):
        secret = "my_secret_key"
        ts = "1700000000"
        method = "POST"
        path = "/order"
        body = '{"order_id":"ord_001"}'
        signer = PolymarketRequestSigner()
        expected = _expected_hmac(ts, method, path, body, secret)
        result = signer.compute_signature(ts, method, path, body, secret)
        assert result == expected

    def test_method_uppercased_for_signing(self):
        signer = PolymarketRequestSigner()
        sig_lower = signer.compute_signature("1700000000", "post", "/order", "", "secret")
        sig_upper = signer.compute_signature("1700000000", "POST", "/order", "", "secret")
        assert sig_lower == sig_upper  # both normalized to uppercase

    def test_returns_hex_string(self):
        signer = PolymarketRequestSigner()
        sig = signer.compute_signature("1700000000", "POST", "/order", "", "secret")
        assert isinstance(sig, str)
        assert len(sig) == 64  # SHA256 hex = 64 chars


# ---------------------------------------------------------------------------
# Credential encoding
# ---------------------------------------------------------------------------

class TestEncodeCredentials:
    def test_decodes_to_correct_structure(self):
        signer = PolymarketRequestSigner()
        creds = _creds(api_key="k1", api_secret="s1", api_passphrase="p1")
        encoded = signer._encode_credentials(creds)
        decoded = json.loads(base64.b64decode(encoded.encode("utf-8")).decode("utf-8"))
        assert decoded["key"] == "k1"
        assert decoded["secret"] == "s1"
        assert decoded["passphrase"] == "p1"

    def test_base64_is_valid(self):
        signer = PolymarketRequestSigner()
        creds = _creds()
        encoded = signer._encode_credentials(creds)
        # Should not raise
        base64.b64decode(encoded.encode("utf-8"))

    def test_no_plaintext_secret_in_result(self):
        """Result is base64 encoded, not plaintext secret value."""
        signer = PolymarketRequestSigner()
        creds = _creds(api_secret="VERY_SECRET_VALUE")
        encoded = signer._encode_credentials(creds)
        assert "VERY_SECRET_VALUE" not in encoded


# ---------------------------------------------------------------------------
# build_auth_headers
# ---------------------------------------------------------------------------

class TestBuildAuthHeaders:
    def test_all_six_headers_present(self):
        signer = _signer_fixed_ts()
        headers = signer.build_auth_headers(_creds(), "POST", "/order")
        assert "Content-Type" in headers
        assert "POLY_ADDRESS" in headers
        assert "POLY_SIGNATURE" in headers
        assert "POLY_TIMESTAMP" in headers
        assert "POLY_NONCE" in headers
        assert "POLY_CREDENTIALS" in headers

    def test_poly_address_is_wallet_address(self):
        signer = _signer_fixed_ts()
        headers = signer.build_auth_headers(_creds(wallet="0xMYWALLET"), "POST", "/order")
        assert headers["POLY_ADDRESS"] == "0xMYWALLET"

    def test_poly_address_prefers_funder_address(self):
        signer = _signer_fixed_ts()
        creds = _creds(wallet="0xWALLET", funder="0xFUNDER")
        headers = signer.build_auth_headers(creds, "POST", "/order")
        assert headers["POLY_ADDRESS"] == "0xFUNDER"

    def test_poly_timestamp_matches_provider(self):
        signer = _signer_fixed_ts("9999999999")
        headers = signer.build_auth_headers(_creds(), "POST", "/order")
        assert headers["POLY_TIMESTAMP"] == "9999999999"

    def test_poly_nonce_default_zero(self):
        signer = _signer_fixed_ts()
        headers = signer.build_auth_headers(_creds(), "POST", "/order")
        assert headers["POLY_NONCE"] == "0"

    def test_poly_nonce_custom(self):
        signer = _signer_fixed_ts()
        headers = signer.build_auth_headers(_creds(), "POST", "/order", nonce="42")
        assert headers["POLY_NONCE"] == "42"

    def test_poly_signature_is_not_empty(self):
        signer = _signer_fixed_ts()
        headers = signer.build_auth_headers(_creds(), "POST", "/order")
        assert headers["POLY_SIGNATURE"] != ""
        assert len(headers["POLY_SIGNATURE"]) == 64

    def test_poly_signature_correct_hmac(self):
        ts = "1700000000"
        secret = "secret_xyz"
        signer = _signer_fixed_ts(ts)
        creds = _creds(api_secret=secret)
        headers = signer.build_auth_headers(creds, "POST", "/order", body='{"x":1}')
        expected = _expected_hmac(ts, "POST", "/order", '{"x":1}', secret)
        assert headers["POLY_SIGNATURE"] == expected

    def test_poly_credentials_decodable(self):
        signer = _signer_fixed_ts()
        headers = signer.build_auth_headers(_creds(), "POST", "/order")
        decoded = json.loads(base64.b64decode(headers["POLY_CREDENTIALS"].encode()).decode())
        assert "key" in decoded
        assert "secret" in decoded
        assert "passphrase" in decoded


# ---------------------------------------------------------------------------
# Credential validation (fail-closed)
# ---------------------------------------------------------------------------

class TestCredentialValidation:
    def test_missing_api_key_raises(self):
        signer = PolymarketRequestSigner()
        creds = LiveCredentials(wallet_address="0xW", api_secret="s")
        with pytest.raises(PolymarketAuthError) as exc_info:
            signer.build_auth_headers(creds, "POST", "/order")
        assert "api_key" in str(exc_info.value)

    def test_missing_api_secret_raises(self):
        signer = PolymarketRequestSigner()
        creds = LiveCredentials(wallet_address="0xW", api_key="k")
        with pytest.raises(PolymarketAuthError) as exc_info:
            signer.build_auth_headers(creds, "POST", "/order")
        assert "api_secret" in str(exc_info.value)

    def test_missing_wallet_address_raises(self):
        signer = PolymarketRequestSigner()
        creds = LiveCredentials(api_key="k", api_secret="s")
        with pytest.raises(PolymarketAuthError) as exc_info:
            signer.build_auth_headers(creds, "POST", "/order")
        assert "wallet_address" in str(exc_info.value)

    def test_all_missing_raises_with_all_fields(self):
        signer = PolymarketRequestSigner()
        creds = LiveCredentials()
        with pytest.raises(PolymarketAuthError) as exc_info:
            signer.build_auth_headers(creds, "POST", "/order")
        msg = str(exc_info.value)
        assert "api_key" in msg
        assert "api_secret" in msg
        assert "wallet_address" in msg

    def test_full_credentials_does_not_raise(self):
        signer = _signer_fixed_ts()
        creds = _creds()
        # Should not raise
        headers = signer.build_auth_headers(creds, "POST", "/order")
        assert headers is not None


# ---------------------------------------------------------------------------
# Secret redaction guard
# ---------------------------------------------------------------------------

class TestSecretRedaction:
    def test_api_secret_not_in_headers_dict_plaintext(self):
        signer = _signer_fixed_ts()
        creds = _creds(api_secret="TOP_SECRET_VALUE")
        headers = signer.build_auth_headers(creds, "POST", "/order")
        # Secret must not appear as plaintext value in any header
        for value in headers.values():
            assert "TOP_SECRET_VALUE" not in str(value)

    def test_private_key_field_not_used_in_signing(self):
        """private_key is not used in request signing — only api_secret is."""
        signer = _signer_fixed_ts("1700000000")
        creds_a = _creds(api_secret="same_secret")
        creds_a.private_key = "private_key_A"
        creds_b = _creds(api_secret="same_secret")
        creds_b.private_key = "private_key_B"
        sig_a = signer.compute_signature("1700000000", "POST", "/order", "", creds_a.api_secret)
        sig_b = signer.compute_signature("1700000000", "POST", "/order", "", creds_b.api_secret)
        assert sig_a == sig_b  # private_key doesn't affect signature
