"""Tests for OrderFillStreamResult — v1.0.3."""
import pytest

from app.domain.live.order_fill_stream_result import OrderFillStreamResult


class TestOrderFillStreamResultDefaults:
    def test_default_update_type_is_empty(self):
        result = OrderFillStreamResult()
        assert result.update_type == ""

    def test_default_order_status_is_empty(self):
        result = OrderFillStreamResult()
        assert result.order_status == ""

    def test_default_terminal_failure_is_false(self):
        result = OrderFillStreamResult()
        assert result.terminal_failure is False

    def test_default_retryable_is_false(self):
        result = OrderFillStreamResult()
        assert result.retryable is False

    def test_default_stream_connected_is_false(self):
        result = OrderFillStreamResult()
        assert result.stream_connected is False

    def test_default_filled_size_is_zero(self):
        result = OrderFillStreamResult()
        assert result.filled_size == 0.0

    def test_default_remaining_size_is_zero(self):
        result = OrderFillStreamResult()
        assert result.remaining_size == 0.0

    def test_default_fill_price_is_zero(self):
        result = OrderFillStreamResult()
        assert result.fill_price == 0.0

    def test_default_order_id_is_empty(self):
        result = OrderFillStreamResult()
        assert result.order_id == ""

    def test_default_client_order_id_is_empty(self):
        result = OrderFillStreamResult()
        assert result.client_order_id == ""

    def test_default_updated_at_is_empty(self):
        result = OrderFillStreamResult()
        assert result.updated_at == ""

    def test_default_source_is_empty(self):
        result = OrderFillStreamResult()
        assert result.source == ""

    def test_default_reject_reason_is_empty(self):
        result = OrderFillStreamResult()
        assert result.reject_reason == ""

    def test_default_raw_update_payload_is_empty_dict(self):
        result = OrderFillStreamResult()
        assert result.raw_update_payload == {}

    def test_default_normalized_update_result_is_empty(self):
        result = OrderFillStreamResult()
        assert result.normalized_update_result == ""


class TestOrderFillStreamResultConstruction:
    def test_full_fill_result(self):
        result = OrderFillStreamResult(
            order_id="ord_001",
            client_order_id="evt_001",
            update_type="full_fill",
            order_status="MATCHED",
            filled_size=10.0,
            remaining_size=0.0,
            fill_price=0.75,
            updated_at="1700000000",
            source="poll",
            stream_connected=True,
        )
        assert result.update_type == "full_fill"
        assert result.filled_size == 10.0
        assert result.remaining_size == 0.0
        assert result.fill_price == 0.75
        assert result.stream_connected is True
        assert result.terminal_failure is False

    def test_partial_fill_result(self):
        result = OrderFillStreamResult(
            order_id="ord_002",
            update_type="partial_fill",
            filled_size=5.0,
            remaining_size=5.0,
        )
        assert result.update_type == "partial_fill"
        assert result.filled_size == 5.0
        assert result.remaining_size == 5.0

    def test_cancelled_result(self):
        result = OrderFillStreamResult(
            order_id="ord_003",
            update_type="cancelled",
            order_status="CANCELLED",
        )
        assert result.update_type == "cancelled"
        assert result.terminal_failure is False

    def test_rejected_result(self):
        result = OrderFillStreamResult(
            order_id="ord_004",
            update_type="rejected",
            order_status="UNMATCHED",
        )
        assert result.update_type == "rejected"

    def test_no_update_result(self):
        result = OrderFillStreamResult(
            order_id="ord_005",
            update_type="no_update",
            order_status="LIVE",
            stream_connected=True,
        )
        assert result.update_type == "no_update"
        assert result.stream_connected is True

    def test_terminal_failure_result(self):
        result = OrderFillStreamResult(
            order_id="ord_006",
            terminal_failure=True,
            reject_reason="auth_error",
        )
        assert result.terminal_failure is True
        assert result.reject_reason == "auth_error"
        assert result.stream_connected is False

    def test_retryable_result(self):
        result = OrderFillStreamResult(
            order_id="ord_007",
            retryable=True,
            reject_reason="timeout",
        )
        assert result.retryable is True
        assert result.terminal_failure is False

    def test_raw_update_payload_mutable_default_isolated(self):
        """Each instance gets its own dict — no shared mutable default."""
        r1 = OrderFillStreamResult()
        r2 = OrderFillStreamResult()
        r1.raw_update_payload["x"] = 1
        assert "x" not in r2.raw_update_payload


class TestOrderFillStreamResultFieldTypes:
    def test_order_id_is_str(self):
        assert isinstance(OrderFillStreamResult(order_id="x").order_id, str)

    def test_update_type_is_str(self):
        assert isinstance(OrderFillStreamResult(update_type="full_fill").update_type, str)

    def test_order_status_is_str(self):
        assert isinstance(OrderFillStreamResult(order_status="LIVE").order_status, str)

    def test_filled_size_is_float(self):
        assert isinstance(OrderFillStreamResult(filled_size=1.0).filled_size, float)

    def test_remaining_size_is_float(self):
        assert isinstance(OrderFillStreamResult(remaining_size=1.0).remaining_size, float)

    def test_fill_price_is_float(self):
        assert isinstance(OrderFillStreamResult(fill_price=0.75).fill_price, float)

    def test_stream_connected_is_bool(self):
        assert isinstance(OrderFillStreamResult(stream_connected=True).stream_connected, bool)

    def test_terminal_failure_is_bool(self):
        assert isinstance(OrderFillStreamResult(terminal_failure=True).terminal_failure, bool)

    def test_retryable_is_bool(self):
        assert isinstance(OrderFillStreamResult(retryable=True).retryable, bool)

    def test_raw_update_payload_is_dict(self):
        assert isinstance(OrderFillStreamResult(raw_update_payload={"a": 1}).raw_update_payload, dict)
