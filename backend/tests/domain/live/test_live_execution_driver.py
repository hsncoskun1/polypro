"""Tests for LiveExecutionDriver — v1.0.4."""
from unittest.mock import MagicMock

import pytest

from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus
from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.adapter_submit_response import AdapterSubmitResponse
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.live_exchange_client import LiveExchangeClient
from app.domain.live.live_execution_driver import LiveExecutionDriver
from app.domain.live.live_execution_driver_context import LiveExecutionDriverContext
from app.domain.live.live_execution_stage import LiveExecutionStage
from app.domain.live.order_fill_stream_result import OrderFillStreamResult
from app.domain.live.polymarket_http_client import PolymarketHttpClient
from app.domain.accounting.accounting_snapshot import AccountingSnapshot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _submit_request(order_id: str = "ord_001", event_key: str = "evt_001") -> AdapterSubmitRequest:
    return AdapterSubmitRequest(
        order_id=order_id,
        event_key=event_key,
        market_id="mkt_001",
        side="buy",
        size=10.0,
        limit_price=0.75,
    )


def _creds() -> LiveCredentials:
    return LiveCredentials(
        wallet_address="0xABC",
        api_key="key",
        api_secret="secret",
    )


def _ctx(
    outbound_allowed: bool = True,
    preflight_passed: bool = True,
    max_poll_attempts: int = 1,
    order_id: str = "ord_001",
    event_key: str = "evt_001",
) -> LiveExecutionDriverContext:
    return LiveExecutionDriverContext(
        event_key=event_key,
        submit_request=_submit_request(order_id=order_id, event_key=event_key),
        credentials=_creds(),
        outbound_allowed=outbound_allowed,
        preflight_passed=preflight_passed,
        max_poll_attempts=max_poll_attempts,
        poll_delay_seconds=0.0,
    )


def _mock_exchange(outcome: AdapterOutcomeStatus = AdapterOutcomeStatus.ADAPTER_SUBMITTED,
                   exchange_order_id: str = "exch_001",
                   terminal: bool = False,
                   retryable: bool = False) -> LiveExchangeClient:
    client = MagicMock(spec=LiveExchangeClient)
    client.submit_order.return_value = AdapterSubmitResponse(
        order_id="ord_001",
        outcome_status=outcome,
        exchange_order_id=exchange_order_id,
        terminal_failure=terminal,
        retryable=retryable,
    )
    return client


def _mock_http(update_type: str = "no_update",
               filled_size: float = 0.0,
               remaining_size: float = 0.0,
               fill_price: float = 0.0,
               terminal_failure: bool = False,
               retryable: bool = False,
               reject_reason: str = "") -> PolymarketHttpClient:
    client = MagicMock(spec=PolymarketHttpClient)
    client.execute_get_fill_stream_update.return_value = OrderFillStreamResult(
        order_id="exch_001",
        update_type=update_type,
        order_status="",
        filled_size=filled_size,
        remaining_size=remaining_size,
        fill_price=fill_price,
        updated_at="1700000000",
        source="poll",
        stream_connected=not terminal_failure and not retryable,
        terminal_failure=terminal_failure,
        retryable=retryable,
        reject_reason=reject_reason,
    )
    return client


def _driver(exchange=None, http=None) -> LiveExecutionDriver:
    return LiveExecutionDriver(
        exchange_client=exchange or _mock_exchange(),
        http_client=http or _mock_http(),
        credentials=_creds(),
    )


# ---------------------------------------------------------------------------
# Preflight / outbound guard
# ---------------------------------------------------------------------------

class TestDriverBlockedByPreflight:
    def test_outbound_not_allowed_stage_preflight_blocked(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=False, preflight_passed=True))
        assert result.driver_stage == LiveExecutionStage.PREFLIGHT_BLOCKED

    def test_preflight_not_passed_stage_preflight_blocked(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=True, preflight_passed=False))
        assert result.driver_stage == LiveExecutionStage.PREFLIGHT_BLOCKED

    def test_both_guards_false_stage_preflight_blocked(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=False, preflight_passed=False))
        assert result.driver_stage == LiveExecutionStage.PREFLIGHT_BLOCKED

    def test_outbound_blocked_has_blocker_reason(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=False, preflight_passed=True))
        assert "outbound_not_allowed" in result.blocker_reasons

    def test_preflight_blocked_has_blocker_reason(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=True, preflight_passed=False))
        assert "preflight_not_passed" in result.blocker_reasons

    def test_both_blocked_both_reasons_present(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=False, preflight_passed=False))
        assert "outbound_not_allowed" in result.blocker_reasons
        assert "preflight_not_passed" in result.blocker_reasons

    def test_blocked_completed_false(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=False))
        assert result.completed is False

    def test_blocked_no_submit_call(self):
        exchange = _mock_exchange()
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=_mock_http(), credentials=_creds())
        driver.run(_ctx(outbound_allowed=False))
        exchange.submit_order.assert_not_called()


# ---------------------------------------------------------------------------
# Submit failure paths
# ---------------------------------------------------------------------------

class TestDriverSubmitFailure:
    def test_submit_terminal_failure_stage(self):
        exchange = _mock_exchange(outcome=AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE, terminal=True)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=_mock_http(), credentials=_creds())
        result = driver.run(_ctx())
        assert result.driver_stage == LiveExecutionStage.TERMINAL_FAILURE
        assert result.terminal_failure is True

    def test_submit_terminal_failure_no_poll(self):
        exchange = _mock_exchange(outcome=AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE, terminal=True)
        http = _mock_http()
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        driver.run(_ctx())
        http.execute_get_fill_stream_update.assert_not_called()

    def test_submit_retryable_stage(self):
        exchange = _mock_exchange(outcome=AdapterOutcomeStatus.ADAPTER_RETRYABLE_FAILURE, retryable=True)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=_mock_http(), credentials=_creds())
        result = driver.run(_ctx())
        assert result.driver_stage == LiveExecutionStage.RETRYABLE_FAILURE
        assert result.retryable is True

    def test_submit_retryable_no_poll(self):
        exchange = _mock_exchange(outcome=AdapterOutcomeStatus.ADAPTER_RETRYABLE_FAILURE, retryable=True)
        http = _mock_http()
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        driver.run(_ctx())
        http.execute_get_fill_stream_update.assert_not_called()

    def test_submit_rejected_terminal_failure(self):
        exchange = _mock_exchange(outcome=AdapterOutcomeStatus.ADAPTER_REJECTED, terminal=True)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=_mock_http(), credentials=_creds())
        result = driver.run(_ctx())
        assert result.terminal_failure is True

    def test_submit_result_captured(self):
        exchange = _mock_exchange(outcome=AdapterOutcomeStatus.ADAPTER_SUBMITTED)
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert "adapter_submitted" in result.submit_result


# ---------------------------------------------------------------------------
# Full fill path
# ---------------------------------------------------------------------------

class TestDriverFullFill:
    def test_full_fill_completed_true(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, remaining_size=0.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.completed is True

    def test_full_fill_stage_filled(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, remaining_size=0.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.driver_stage == LiveExecutionStage.FILLED

    def test_full_fill_last_filled_size(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.last_filled_size == 10.0

    def test_full_fill_last_fill_price(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.last_fill_price == 0.75

    def test_full_fill_terminal_failure_false(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.terminal_failure is False

    def test_full_fill_update_result_captured(self):
        exchange = _mock_exchange()
        http = _mock_http("full_fill", filled_size=10.0)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.update_result == "full_fill"
        assert result.last_update_status == "full_fill"

    def test_full_fill_accounting_result_is_snapshot(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert isinstance(result.accounting_result, AccountingSnapshot)

    def test_full_fill_accounting_filled_size(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.accounting_result.filled_size == 10.0

    def test_full_fill_accounting_entry_fill_price(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.accounting_result.entry_fill_price == 0.75

    def test_full_fill_accounting_realized_pnl_zero_at_entry(self):
        # At entry fill with current_price == fill_price, realized_pnl is 0.0 (position open)
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.accounting_result.realized_pnl == 0.0

    def test_full_fill_accounting_unrealized_pnl_zero_when_current_equals_fill(self):
        # current_price is set to fill_price in driver, so unrealized_pnl == 0.0
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.accounting_result.unrealized_pnl == 0.0

    def test_full_fill_accounting_pnl_fields_on_result(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0, fill_price=0.75)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.realized_pnl == 0.0
        assert result.unrealized_pnl == 0.0
        assert result.current_balance == 0.0


# ---------------------------------------------------------------------------
# Partial fill path
# ---------------------------------------------------------------------------

class TestDriverPartialFill:
    def test_partial_fill_completed_false(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("partial_fill", filled_size=5.0, remaining_size=5.0, fill_price=0.74)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.completed is False

    def test_partial_fill_stage_fill_in_progress(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("partial_fill", filled_size=5.0, remaining_size=5.0)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.driver_stage == LiveExecutionStage.FILL_IN_PROGRESS

    def test_partial_fill_last_filled_size(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("partial_fill", filled_size=5.0, fill_price=0.74)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.last_filled_size == 5.0


# ---------------------------------------------------------------------------
# No update path
# ---------------------------------------------------------------------------

class TestDriverNoUpdate:
    def test_no_update_completed_false(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.completed is False

    def test_no_update_stage_submitted(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.driver_stage == LiveExecutionStage.SUBMITTED

    def test_no_update_last_filled_size_zero(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.last_filled_size == 0.0


# ---------------------------------------------------------------------------
# Cancelled path
# ---------------------------------------------------------------------------

class TestDriverCancelled:
    def test_cancelled_stage_cancelled(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("cancelled")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.driver_stage == LiveExecutionStage.CANCELLED

    def test_cancelled_completed_true(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("cancelled")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.completed is True


# ---------------------------------------------------------------------------
# Rejected path
# ---------------------------------------------------------------------------

class TestDriverRejected:
    def test_rejected_stage_terminal_failure(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("rejected")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.driver_stage == LiveExecutionStage.TERMINAL_FAILURE

    def test_rejected_terminal_failure_true(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("rejected")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.terminal_failure is True

    def test_rejected_completed_false(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("rejected")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.completed is False


# ---------------------------------------------------------------------------
# Poll error paths
# ---------------------------------------------------------------------------

class TestDriverPollErrors:
    def test_poll_auth_error_terminal_failure(self):
        exchange = _mock_exchange()
        http = _mock_http(terminal_failure=True, reject_reason="auth_error")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.terminal_failure is True
        assert result.driver_stage == LiveExecutionStage.TERMINAL_FAILURE

    def test_poll_timeout_retryable(self):
        exchange = _mock_exchange()
        http = _mock_http(retryable=True, reject_reason="timeout")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.retryable is True
        assert result.driver_stage == LiveExecutionStage.RETRYABLE_FAILURE

    def test_poll_unknown_update_type_terminal(self):
        exchange = _mock_exchange()
        http = _mock_http("unknown")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.terminal_failure is True

    def test_poll_auth_error_no_fake_completed(self):
        exchange = _mock_exchange()
        http = _mock_http(terminal_failure=True)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.completed is False


# ---------------------------------------------------------------------------
# Poll attempt counting
# ---------------------------------------------------------------------------

class TestDriverPollAttempts:
    def test_poll_attempts_counted_single(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx(max_poll_attempts=1))
        assert result.poll_attempts == 1

    def test_poll_attempts_counted_multiple(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx(max_poll_attempts=3))
        assert result.poll_attempts == 3

    def test_poll_stops_early_on_full_fill(self):
        exchange = _mock_exchange()
        http = _mock_http("full_fill", filled_size=10.0)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx(max_poll_attempts=5))
        assert result.poll_attempts == 1  # stops after first terminal update

    def test_poll_stops_early_on_terminal_failure(self):
        exchange = _mock_exchange()
        http = _mock_http(terminal_failure=True)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx(max_poll_attempts=5))
        assert result.poll_attempts == 1

    def test_blocked_poll_attempts_zero(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=False))
        assert result.poll_attempts == 0


# ---------------------------------------------------------------------------
# Reconciliation result
# ---------------------------------------------------------------------------

class TestDriverReconciliationResult:
    def test_reconciliation_result_populated_on_full_fill(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.reconciliation_result != ""

    def test_reconciliation_result_no_events_on_no_update(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.reconciliation_result == "no_events"

    def test_full_fill_reconciliation_terminal_state(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("full_fill", filled_size=10.0)
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.reconciliation_result == "terminal_state"


# ---------------------------------------------------------------------------
# Identity fields
# ---------------------------------------------------------------------------

class TestDriverIdentityFields:
    def test_event_key_carried(self):
        driver = _driver(exchange=_mock_exchange(), http=_mock_http("no_update"))
        result = driver.run(_ctx(event_key="evt_abc"))
        assert result.event_key == "evt_abc"

    def test_order_id_from_exchange_response(self):
        exchange = _mock_exchange(exchange_order_id="exch_999")
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.order_id == "exch_999"

    def test_order_id_falls_back_to_request(self):
        exchange = _mock_exchange(exchange_order_id="")  # no exchange id
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx(order_id="ord_fallback"))
        assert result.order_id == "ord_fallback"

    def test_client_order_id_is_event_key(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx(event_key="evt_xyz"))
        assert result.client_order_id == "evt_xyz"


# ---------------------------------------------------------------------------
# Raw driver trace audit
# ---------------------------------------------------------------------------

class TestDriverTrace:
    def test_trace_populated_on_success(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert len(result.raw_driver_trace) > 0

    def test_trace_contains_submit_entry(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert any("submit" in entry for entry in result.raw_driver_trace)

    def test_trace_contains_poll_entry(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert any("poll" in entry for entry in result.raw_driver_trace)

    def test_trace_populated_on_blocked(self):
        driver = _driver()
        result = driver.run(_ctx(outbound_allowed=False))
        assert len(result.raw_driver_trace) > 0


# ---------------------------------------------------------------------------
# No fake success guarantee
# ---------------------------------------------------------------------------

class TestDriverNoFakeSuccess:
    def test_blocked_no_completed(self):
        result = _driver().run(_ctx(outbound_allowed=False))
        assert result.completed is False
        assert result.last_filled_size == 0.0

    def test_submit_failure_no_completed(self):
        exchange = _mock_exchange(terminal=True)
        result = LiveExecutionDriver(exchange_client=exchange, http_client=_mock_http(), credentials=_creds()).run(_ctx())
        assert result.completed is False

    def test_poll_error_no_completed(self):
        exchange = _mock_exchange()
        http = _mock_http(terminal_failure=True)
        result = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds()).run(_ctx())
        assert result.completed is False
        assert result.last_filled_size == 0.0

    def test_no_update_no_fill_price(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        result = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds()).run(_ctx())
        assert result.last_fill_price == 0.0
        assert result.last_filled_size == 0.0


# ---------------------------------------------------------------------------
# Accounting result — no-fill cases
# ---------------------------------------------------------------------------

class TestDriverAccountingNoFill:
    def test_no_update_accounting_result_is_snapshot(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert isinstance(result.accounting_result, AccountingSnapshot)

    def test_no_update_accounting_filled_size_zero(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.accounting_result.filled_size == 0.0

    def test_no_update_accounting_pnl_all_zero(self):
        exchange = _mock_exchange()
        http = _mock_http("no_update")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.accounting_result.realized_pnl == 0.0
        assert result.accounting_result.unrealized_pnl == 0.0
        assert result.accounting_result.current_balance == 0.0

    def test_cancelled_accounting_result_is_snapshot(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("cancelled")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert isinstance(result.accounting_result, AccountingSnapshot)

    def test_cancelled_accounting_pnl_all_zero(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("cancelled")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.accounting_result.realized_pnl == 0.0
        assert result.accounting_result.unrealized_pnl == 0.0

    def test_rejected_accounting_result_is_snapshot(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("rejected")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert isinstance(result.accounting_result, AccountingSnapshot)

    def test_rejected_accounting_pnl_all_zero(self):
        exchange = _mock_exchange(exchange_order_id="exch_001")
        http = _mock_http("rejected")
        driver = LiveExecutionDriver(exchange_client=exchange, http_client=http, credentials=_creds())
        result = driver.run(_ctx())
        assert result.accounting_result.realized_pnl == 0.0
        assert result.accounting_result.unrealized_pnl == 0.0
