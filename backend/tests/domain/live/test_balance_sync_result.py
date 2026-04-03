"""Tests for BalanceSyncResult — v1.0.2."""
import pytest

from app.domain.live.balance_sync_result import BalanceSyncResult


class TestBalanceSyncResultDefaults:
    def test_default_sync_success_is_false(self):
        result = BalanceSyncResult()
        assert result.sync_success is False

    def test_default_terminal_failure_is_false(self):
        result = BalanceSyncResult()
        assert result.terminal_failure is False

    def test_default_retryable_is_false(self):
        result = BalanceSyncResult()
        assert result.retryable is False

    def test_default_balances_are_zero(self):
        result = BalanceSyncResult()
        assert result.total_balance == 0.0
        assert result.available_balance == 0.0
        assert result.current_balance == 0.0

    def test_default_currency_is_empty(self):
        result = BalanceSyncResult()
        assert result.currency == ""

    def test_default_synced_at_is_empty(self):
        result = BalanceSyncResult()
        assert result.synced_at == ""

    def test_default_reject_reason_is_empty(self):
        result = BalanceSyncResult()
        assert result.reject_reason == ""

    def test_default_raw_balance_payload_is_empty_dict(self):
        result = BalanceSyncResult()
        assert result.raw_balance_payload == {}

    def test_default_normalized_balance_result_is_empty(self):
        result = BalanceSyncResult()
        assert result.normalized_balance_result == ""


class TestBalanceSyncResultConstruction:
    def test_success_result_all_fields(self):
        result = BalanceSyncResult(
            total_balance=250.50,
            available_balance=200.00,
            current_balance=175.00,
            currency="USDC",
            synced_at="1700000000",
            sync_success=True,
            retryable=False,
            terminal_failure=False,
            reject_reason="",
            raw_balance_payload={"balance": "250.50"},
            normalized_balance_result="balance=250.5 USDC synced_at=1700000000",
        )
        assert result.total_balance == 250.50
        assert result.available_balance == 200.00
        assert result.current_balance == 175.00
        assert result.currency == "USDC"
        assert result.sync_success is True
        assert result.terminal_failure is False
        assert result.retryable is False

    def test_failure_result_terminal(self):
        result = BalanceSyncResult(
            sync_success=False,
            terminal_failure=True,
            reject_reason="auth_error",
        )
        assert result.sync_success is False
        assert result.terminal_failure is True
        assert result.reject_reason == "auth_error"
        assert result.total_balance == 0.0

    def test_failure_result_retryable(self):
        result = BalanceSyncResult(
            sync_success=False,
            retryable=True,
            terminal_failure=False,
            reject_reason="timeout",
        )
        assert result.retryable is True
        assert result.terminal_failure is False

    def test_raw_balance_payload_mutable_default_isolated(self):
        """Each instance gets its own dict — no shared mutable default."""
        r1 = BalanceSyncResult()
        r2 = BalanceSyncResult()
        r1.raw_balance_payload["x"] = 1
        assert "x" not in r2.raw_balance_payload

    def test_sync_success_false_when_terminal_failure_true(self):
        """Invariant: terminal_failure=True implies sync_success=False."""
        result = BalanceSyncResult(sync_success=False, terminal_failure=True)
        assert result.sync_success is False

    def test_sync_success_false_when_retryable_true(self):
        """Invariant: retryable=True implies sync_success=False."""
        result = BalanceSyncResult(sync_success=False, retryable=True)
        assert result.sync_success is False


class TestBalanceSyncResultFieldTypes:
    def test_total_balance_is_float(self):
        result = BalanceSyncResult(total_balance=100.0)
        assert isinstance(result.total_balance, float)

    def test_available_balance_is_float(self):
        result = BalanceSyncResult(available_balance=50.0)
        assert isinstance(result.available_balance, float)

    def test_current_balance_is_float(self):
        result = BalanceSyncResult(current_balance=25.0)
        assert isinstance(result.current_balance, float)

    def test_sync_success_is_bool(self):
        result = BalanceSyncResult(sync_success=True)
        assert isinstance(result.sync_success, bool)

    def test_terminal_failure_is_bool(self):
        result = BalanceSyncResult(terminal_failure=True)
        assert isinstance(result.terminal_failure, bool)

    def test_retryable_is_bool(self):
        result = BalanceSyncResult(retryable=True)
        assert isinstance(result.retryable, bool)

    def test_currency_is_str(self):
        result = BalanceSyncResult(currency="USDC")
        assert isinstance(result.currency, str)

    def test_synced_at_is_str(self):
        result = BalanceSyncResult(synced_at="1700000000")
        assert isinstance(result.synced_at, str)

    def test_reject_reason_is_str(self):
        result = BalanceSyncResult(reject_reason="auth_error")
        assert isinstance(result.reject_reason, str)

    def test_raw_balance_payload_is_dict(self):
        result = BalanceSyncResult(raw_balance_payload={"balance": "10.0"})
        assert isinstance(result.raw_balance_payload, dict)
