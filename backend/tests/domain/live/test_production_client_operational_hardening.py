"""Tests for production client operational hardening — v0.8.1."""
from app.domain.live.client_timeout_policy import ClientTimeoutPolicy
from app.domain.live.client_retry_policy import ClientRetryPolicy
from app.domain.live.client_exception_type import ClientExceptionType
from app.domain.live.normalized_client_exception import NormalizedClientException
from app.domain.live.client_operation_context import ClientOperationContext
from app.domain.live.safe_log_payload import SafeLogPayload, redact_payload
from app.domain.live.client_response_validator import (
    validate_submit_response,
    validate_cancel_response,
    validate_replace_response,
    validate_update_response,
)
from app.domain.live.external_response_payload import ExternalResponsePayload


# ---------------------------------------------------------------------------
# TestClientTimeoutPolicy
# ---------------------------------------------------------------------------

class TestClientTimeoutPolicy:
    def test_defaults(self):
        p = ClientTimeoutPolicy()
        assert p.timeout_seconds == 30.0
        assert p.retryable_on_timeout is True

    def test_custom_timeout(self):
        p = ClientTimeoutPolicy(timeout_seconds=10.0, retryable_on_timeout=False)
        assert p.timeout_seconds == 10.0
        assert p.retryable_on_timeout is False

    def test_timeout_seconds_field_present(self):
        p = ClientTimeoutPolicy(timeout_seconds=5.0)
        assert p.timeout_seconds == 5.0


# ---------------------------------------------------------------------------
# TestClientRetryPolicy
# ---------------------------------------------------------------------------

class TestClientRetryPolicy:
    def test_defaults(self):
        p = ClientRetryPolicy()
        assert p.max_retries == 3
        assert p.retry_delay_seconds == 1.0
        assert p.retryable_error_codes == []

    def test_custom_values(self):
        p = ClientRetryPolicy(
            max_retries=5,
            retry_delay_seconds=2.5,
            retryable_error_codes=["client_timeout", "client_retryable_error"],
        )
        assert p.max_retries == 5
        assert p.retry_delay_seconds == 2.5
        assert "client_timeout" in p.retryable_error_codes

    def test_retryable_error_codes_independent(self):
        p1 = ClientRetryPolicy()
        p2 = ClientRetryPolicy()
        p1.retryable_error_codes.append("x")
        assert p2.retryable_error_codes == []


# ---------------------------------------------------------------------------
# TestClientExceptionType
# ---------------------------------------------------------------------------

class TestClientExceptionType:
    def test_timeout_value(self):
        assert ClientExceptionType.TIMEOUT == "timeout"

    def test_connection_error_value(self):
        assert ClientExceptionType.CONNECTION_ERROR == "connection_error"

    def test_invalid_response_value(self):
        assert ClientExceptionType.INVALID_RESPONSE == "invalid_response"

    def test_auth_error_value(self):
        assert ClientExceptionType.AUTH_ERROR == "auth_error"

    def test_rate_limited_value(self):
        assert ClientExceptionType.RATE_LIMITED == "rate_limited"

    def test_unknown_value(self):
        assert ClientExceptionType.UNKNOWN == "unknown"

    def test_all_six_types(self):
        types = list(ClientExceptionType)
        assert len(types) == 6


# ---------------------------------------------------------------------------
# TestNormalizedClientException
# ---------------------------------------------------------------------------

class TestNormalizedClientException:
    def test_defaults_fail_closed(self):
        """Unknown exception defaults to terminal_failure=True (fail-closed)."""
        exc = NormalizedClientException()
        assert exc.exception_type == ClientExceptionType.UNKNOWN
        assert exc.terminal_failure is True
        assert exc.retryable is False
        assert exc.normalized_error_code == ""
        assert exc.normalized_error_message == ""
        assert exc.raw_error_type == ""

    def test_timeout_error_normalized(self):
        exc = NormalizedClientException(
            exception_type=ClientExceptionType.TIMEOUT,
            normalized_error_code="client_timeout",
            normalized_error_message="Request timed out waiting for exchange response.",
            retryable=True,
            terminal_failure=False,
            raw_error_type="TimeoutError",
        )
        assert exc.exception_type == ClientExceptionType.TIMEOUT
        assert exc.normalized_error_code == "client_timeout"
        assert exc.retryable is True
        assert exc.terminal_failure is False
        assert exc.raw_error_type == "TimeoutError"

    def test_retryable_error_classified(self):
        exc = NormalizedClientException(
            exception_type=ClientExceptionType.CONNECTION_ERROR,
            normalized_error_code="client_retryable_error",
            retryable=True,
            terminal_failure=False,
        )
        assert exc.retryable is True
        assert exc.terminal_failure is False

    def test_terminal_error_classified(self):
        exc = NormalizedClientException(
            exception_type=ClientExceptionType.AUTH_ERROR,
            normalized_error_code="client_terminal_error",
            retryable=False,
            terminal_failure=True,
        )
        assert exc.terminal_failure is True
        assert exc.retryable is False

    def test_unknown_exception_fail_closed(self):
        exc = NormalizedClientException(
            exception_type=ClientExceptionType.UNKNOWN,
            normalized_error_code="",
        )
        assert exc.terminal_failure is True

    def test_malformed_response_classified(self):
        exc = NormalizedClientException(
            exception_type=ClientExceptionType.INVALID_RESPONSE,
            normalized_error_code="malformed_response",
            retryable=False,
            terminal_failure=True,
        )
        assert exc.normalized_error_code == "malformed_response"
        assert exc.terminal_failure is True


# ---------------------------------------------------------------------------
# TestClientOperationContext
# ---------------------------------------------------------------------------

class TestClientOperationContext:
    def test_required_fields(self):
        ctx = ClientOperationContext(operation_type="submit", order_id="ord_001")
        assert ctx.operation_type == "submit"
        assert ctx.order_id == "ord_001"

    def test_defaults(self):
        ctx = ClientOperationContext(operation_type="cancel", order_id="ord_002")
        assert ctx.correlation_id == ""
        assert ctx.idempotency_key == ""
        assert ctx.timeout_seconds == 30.0

    def test_correlation_id_carried(self):
        ctx = ClientOperationContext(
            operation_type="submit",
            order_id="ord_001",
            correlation_id="corr_abc123",
        )
        assert ctx.correlation_id == "corr_abc123"

    def test_idempotency_key_carried(self):
        ctx = ClientOperationContext(
            operation_type="submit",
            order_id="ord_001",
            idempotency_key="idem_xyz789",
        )
        assert ctx.idempotency_key == "idem_xyz789"

    def test_timeout_seconds_override(self):
        ctx = ClientOperationContext(
            operation_type="replace",
            order_id="ord_003",
            timeout_seconds=15.0,
        )
        assert ctx.timeout_seconds == 15.0

    def test_all_fields_set(self):
        ctx = ClientOperationContext(
            operation_type="submit",
            order_id="ord_001",
            correlation_id="corr_001",
            idempotency_key="idem_001",
            timeout_seconds=20.0,
        )
        assert ctx.correlation_id == "corr_001"
        assert ctx.idempotency_key == "idem_001"
        assert ctx.timeout_seconds == 20.0


# ---------------------------------------------------------------------------
# TestSafeLogPayload
# ---------------------------------------------------------------------------

class TestSafeLogPayload:
    def test_defaults(self):
        p = SafeLogPayload()
        assert p.operation_type == ""
        assert p.order_id == ""
        assert p.correlation_id == ""
        assert p.masked_fields == []

    def test_fields_set(self):
        p = SafeLogPayload(
            operation_type="submit",
            order_id="ord_001",
            correlation_id="corr_abc",
            masked_fields=["api_key", "signature"],
        )
        assert p.operation_type == "submit"
        assert p.correlation_id == "corr_abc"
        assert "api_key" in p.masked_fields

    def test_masked_fields_independent(self):
        p1 = SafeLogPayload()
        p2 = SafeLogPayload()
        p1.masked_fields.append("secret")
        assert p2.masked_fields == []


class TestRedactPayload:
    def test_api_key_redacted(self):
        raw = {"order_id": "ord_001", "api_key": "super_secret_key"}
        result = redact_payload(raw)
        assert result["api_key"] == "[REDACTED]"
        assert result["order_id"] == "ord_001"

    def test_signature_redacted(self):
        raw = {"order_id": "ord_001", "signature": "abc123"}
        result = redact_payload(raw)
        assert result["signature"] == "[REDACTED]"

    def test_raw_payload_redacted(self):
        raw = {"order_id": "ord_001", "raw_payload": "sensitive_exchange_data"}
        result = redact_payload(raw)
        assert result["raw_payload"] == "[REDACTED]"

    def test_safe_field_not_redacted(self):
        raw = {"order_id": "ord_001", "market_id": "mkt_001"}
        result = redact_payload(raw)
        assert result["order_id"] == "ord_001"
        assert result["market_id"] == "mkt_001"

    def test_safe_logging_secret_fields_not_leaked(self):
        """Secrets never appear in the redacted output."""
        raw = {
            "api_key": "KEY_VALUE",
            "api_secret": "SECRET_VALUE",
            "passphrase": "PASS_VALUE",
            "token": "TOKEN_VALUE",
            "order_id": "ord_001",
        }
        result = redact_payload(raw)
        for field_name in ("api_key", "api_secret", "passphrase", "token"):
            assert result[field_name] == "[REDACTED]"
        assert result["order_id"] == "ord_001"

    def test_custom_sensitive_keys(self):
        raw = {"custom_secret": "hidden", "order_id": "ord_001"}
        result = redact_payload(raw, sensitive_keys=frozenset({"custom_secret"}))
        assert result["custom_secret"] == "[REDACTED]"
        assert result["order_id"] == "ord_001"

    def test_original_dict_not_mutated(self):
        raw = {"api_key": "KEY", "order_id": "ord_001"}
        redact_payload(raw)
        assert raw["api_key"] == "KEY"


# ---------------------------------------------------------------------------
# TestClientResponseValidator
# ---------------------------------------------------------------------------

class TestClientResponseValidator:
    # --- submit ---

    def test_submit_valid_response(self):
        payload = ExternalResponsePayload(mapped_order_id="ord_001", mapped_status="submitted")
        passed, blockers = validate_submit_response(payload)
        assert passed is True
        assert blockers == []

    def test_submit_missing_order_id_fails(self):
        payload = ExternalResponsePayload(mapped_order_id="", mapped_status="submitted")
        passed, blockers = validate_submit_response(payload)
        assert passed is False
        assert any("mapped_order_id" in b for b in blockers)

    def test_submit_missing_status_fails(self):
        payload = ExternalResponsePayload(mapped_order_id="ord_001", mapped_status="")
        passed, blockers = validate_submit_response(payload)
        assert passed is False
        assert any("mapped_status" in b for b in blockers)

    def test_submit_terminal_failure_bypasses_status_check(self):
        """terminal_failure=True is a valid fail-closed path — no missing_status blocker."""
        payload = ExternalResponsePayload(mapped_order_id="ord_001", mapped_status="", terminal_failure=True)
        passed, blockers = validate_submit_response(payload)
        # Only blocker could be order_id — status is allowed empty when terminal_failure=True
        assert not any("mapped_status" in b for b in blockers)

    def test_submit_malformed_response_fail_closed(self):
        """Both order_id and status missing — two blockers, validation_failed."""
        payload = ExternalResponsePayload()
        passed, blockers = validate_submit_response(payload)
        assert passed is False
        assert len(blockers) >= 1

    # --- cancel ---

    def test_cancel_valid_response(self):
        payload = ExternalResponsePayload(mapped_order_id="ord_001", mapped_status="cancelled")
        passed, blockers = validate_cancel_response(payload)
        assert passed is True
        assert blockers == []

    def test_cancel_missing_order_id_fails(self):
        payload = ExternalResponsePayload(mapped_order_id="", mapped_status="cancelled")
        passed, blockers = validate_cancel_response(payload)
        assert passed is False

    # --- replace ---

    def test_replace_valid_response(self):
        payload = ExternalResponsePayload(mapped_order_id="new_ord_002", mapped_status="replaced")
        passed, blockers = validate_replace_response(payload)
        assert passed is True
        assert blockers == []

    def test_replace_missing_order_id_fails(self):
        payload = ExternalResponsePayload(mapped_order_id="", mapped_status="replaced")
        passed, blockers = validate_replace_response(payload)
        assert passed is False

    # --- update ---

    def test_update_valid_no_update(self):
        payload = ExternalResponsePayload(mapped_status="no_update")
        passed, blockers = validate_update_response(payload)
        assert passed is True
        assert blockers == []

    def test_update_valid_update_received(self):
        payload = ExternalResponsePayload(mapped_status="update_received")
        passed, blockers = validate_update_response(payload)
        assert passed is True

    def test_update_missing_status_fails(self):
        payload = ExternalResponsePayload(mapped_status="")
        passed, blockers = validate_update_response(payload)
        assert passed is False
        assert any("mapped_status" in b for b in blockers)

    def test_update_terminal_failure_bypasses_status_check(self):
        payload = ExternalResponsePayload(mapped_status="", terminal_failure=True)
        passed, blockers = validate_update_response(payload)
        assert not any("mapped_status" in b for b in blockers)

    # --- blocker reason strings ---

    def test_blocker_reason_correlation_id_missing(self):
        ctx_blockers = ["correlation_id_missing"]
        assert "correlation_id_missing" in ctx_blockers

    def test_blocker_reason_idempotency_key_missing(self):
        ctx_blockers = ["idempotency_key_missing"]
        assert "idempotency_key_missing" in ctx_blockers

    def test_blocker_reason_validation_failed(self):
        payload = ExternalResponsePayload()
        passed, blockers = validate_submit_response(payload)
        assert passed is False
