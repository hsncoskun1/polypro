"""Tests for live exchange client adapter foundation — v0.7.8."""
import pytest
from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus
from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.adapter_submit_response import AdapterSubmitResponse
from app.domain.live.adapter_cancel_request import AdapterCancelRequest
from app.domain.live.adapter_cancel_response import AdapterCancelResponse
from app.domain.live.adapter_replace_request import AdapterReplaceRequest
from app.domain.live.adapter_replace_response import AdapterReplaceResponse
from app.domain.live.adapter_order_update import AdapterOrderUpdate
from app.domain.live.live_exchange_client import LiveExchangeClient
from app.domain.live.mock_live_exchange_client import MockLiveExchangeClient


# ---------------------------------------------------------------------------
# TestAdapterOutcomeStatus
# ---------------------------------------------------------------------------

class TestAdapterOutcomeStatus:
    def test_adapter_submitted(self):
        assert AdapterOutcomeStatus.ADAPTER_SUBMITTED == "adapter_submitted"

    def test_adapter_accepted(self):
        assert AdapterOutcomeStatus.ADAPTER_ACCEPTED == "adapter_accepted"

    def test_adapter_rejected(self):
        assert AdapterOutcomeStatus.ADAPTER_REJECTED == "adapter_rejected"

    def test_adapter_retryable_failure(self):
        assert AdapterOutcomeStatus.ADAPTER_RETRYABLE_FAILURE == "adapter_retryable_failure"

    def test_adapter_terminal_failure(self):
        assert AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE == "adapter_terminal_failure"

    def test_adapter_update_received(self):
        assert AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED == "adapter_update_received"

    def test_adapter_no_update(self):
        assert AdapterOutcomeStatus.ADAPTER_NO_UPDATE == "adapter_no_update"

    def test_is_str_enum(self):
        assert isinstance(AdapterOutcomeStatus.ADAPTER_SUBMITTED, str)


# ---------------------------------------------------------------------------
# TestAdapterSubmitRequest
# ---------------------------------------------------------------------------

class TestAdapterSubmitRequest:
    def test_required_fields(self):
        r = AdapterSubmitRequest(
            order_id="ord_001",
            event_key="evt_001",
            market_id="mkt_001",
            side="buy",
            size=10.0,
            limit_price=0.75,
        )
        assert r.order_id == "ord_001"
        assert r.event_key == "evt_001"
        assert r.market_id == "mkt_001"
        assert r.side == "buy"
        assert r.size == 10.0
        assert r.limit_price == 0.75


# ---------------------------------------------------------------------------
# TestAdapterSubmitResponse
# ---------------------------------------------------------------------------

class TestAdapterSubmitResponse:
    def test_required_fields(self):
        r = AdapterSubmitResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_SUBMITTED,
        )
        assert r.order_id == "ord_001"
        assert r.outcome_status == AdapterOutcomeStatus.ADAPTER_SUBMITTED

    def test_defaults(self):
        r = AdapterSubmitResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_SUBMITTED,
        )
        assert r.exchange_order_id == ""
        assert r.reject_reason == ""
        assert r.retryable is False
        assert r.terminal_failure is False

    def test_rejected_carries_reason(self):
        r = AdapterSubmitResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_REJECTED,
            reject_reason="insufficient_funds",
        )
        assert r.reject_reason == "insufficient_funds"

    def test_retryable_fields(self):
        r = AdapterSubmitResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_RETRYABLE_FAILURE,
            retryable=True,
        )
        assert r.retryable is True
        assert r.terminal_failure is False

    def test_terminal_fields(self):
        r = AdapterSubmitResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE,
            terminal_failure=True,
        )
        assert r.terminal_failure is True
        assert r.retryable is False


# ---------------------------------------------------------------------------
# TestAdapterCancelRequest
# ---------------------------------------------------------------------------

class TestAdapterCancelRequest:
    def test_required_fields(self):
        r = AdapterCancelRequest(order_id="ord_001", event_key="evt_001")
        assert r.order_id == "ord_001"
        assert r.event_key == "evt_001"


# ---------------------------------------------------------------------------
# TestAdapterCancelResponse
# ---------------------------------------------------------------------------

class TestAdapterCancelResponse:
    def test_required_fields(self):
        r = AdapterCancelResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_ACCEPTED,
        )
        assert r.order_id == "ord_001"
        assert r.outcome_status == AdapterOutcomeStatus.ADAPTER_ACCEPTED

    def test_defaults(self):
        r = AdapterCancelResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_ACCEPTED,
        )
        assert r.reject_reason == ""
        assert r.retryable is False
        assert r.terminal_failure is False


# ---------------------------------------------------------------------------
# TestAdapterReplaceRequest
# ---------------------------------------------------------------------------

class TestAdapterReplaceRequest:
    def test_required_fields(self):
        r = AdapterReplaceRequest(
            order_id="ord_001",
            event_key="evt_001",
            new_limit_price=0.80,
            new_size=15.0,
        )
        assert r.order_id == "ord_001"
        assert r.new_limit_price == 0.80
        assert r.new_size == 15.0


# ---------------------------------------------------------------------------
# TestAdapterReplaceResponse
# ---------------------------------------------------------------------------

class TestAdapterReplaceResponse:
    def test_required_fields(self):
        r = AdapterReplaceResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_SUBMITTED,
        )
        assert r.order_id == "ord_001"
        assert r.outcome_status == AdapterOutcomeStatus.ADAPTER_SUBMITTED

    def test_defaults(self):
        r = AdapterReplaceResponse(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_SUBMITTED,
        )
        assert r.new_exchange_order_id == ""
        assert r.reject_reason == ""
        assert r.retryable is False
        assert r.terminal_failure is False


# ---------------------------------------------------------------------------
# TestAdapterOrderUpdate
# ---------------------------------------------------------------------------

class TestAdapterOrderUpdate:
    def test_required_fields(self):
        u = AdapterOrderUpdate(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED,
        )
        assert u.order_id == "ord_001"
        assert u.outcome_status == AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED

    def test_defaults(self):
        u = AdapterOrderUpdate(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_NO_UPDATE,
        )
        assert u.filled_size == 0.0
        assert u.remaining_size == 0.0
        assert u.update_timestamp == ""

    def test_fill_fields(self):
        u = AdapterOrderUpdate(
            order_id="ord_001",
            outcome_status=AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED,
            filled_size=5.0,
            remaining_size=5.0,
            update_timestamp="2026-04-02T10:00:00",
        )
        assert u.filled_size == 5.0
        assert u.remaining_size == 5.0
        assert u.update_timestamp == "2026-04-02T10:00:00"


# ---------------------------------------------------------------------------
# TestLiveExchangeClientAbstract
# ---------------------------------------------------------------------------

class TestLiveExchangeClientAbstract:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            LiveExchangeClient()  # type: ignore

    def test_mock_is_subclass(self):
        assert issubclass(MockLiveExchangeClient, LiveExchangeClient)

    def test_mock_is_instance(self):
        client = MockLiveExchangeClient()
        assert isinstance(client, LiveExchangeClient)


# ---------------------------------------------------------------------------
# TestMockLiveExchangeClient — Default Outcomes
# ---------------------------------------------------------------------------

class TestMockDefaultOutcomes:
    def setup_method(self):
        self.client = MockLiveExchangeClient()
        self.submit_req = AdapterSubmitRequest(
            order_id="ord_001", event_key="evt_001",
            market_id="mkt_001", side="buy", size=10.0, limit_price=0.75,
        )
        self.cancel_req = AdapterCancelRequest(order_id="ord_001", event_key="evt_001")
        self.replace_req = AdapterReplaceRequest(
            order_id="ord_001", event_key="evt_001",
            new_limit_price=0.80, new_size=15.0,
        )

    def test_submit_default_outcome(self):
        resp = self.client.submit_order(self.submit_req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_SUBMITTED

    def test_submit_carries_order_id(self):
        resp = self.client.submit_order(self.submit_req)
        assert resp.order_id == "ord_001"

    def test_cancel_default_outcome(self):
        resp = self.client.cancel_order(self.cancel_req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_ACCEPTED

    def test_cancel_carries_order_id(self):
        resp = self.client.cancel_order(self.cancel_req)
        assert resp.order_id == "ord_001"

    def test_replace_default_outcome(self):
        resp = self.client.replace_order(self.replace_req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_SUBMITTED

    def test_replace_carries_order_id(self):
        resp = self.client.replace_order(self.replace_req)
        assert resp.order_id == "ord_001"

    def test_get_order_update_default_no_update(self):
        update = self.client.get_order_update("ord_001")
        assert update.outcome_status == AdapterOutcomeStatus.ADAPTER_NO_UPDATE

    def test_get_order_update_carries_order_id(self):
        update = self.client.get_order_update("ord_001")
        assert update.order_id == "ord_001"


# ---------------------------------------------------------------------------
# TestMockLiveExchangeClient — Configurable Outcomes
# ---------------------------------------------------------------------------

class TestMockConfigurableOutcomes:
    def test_submit_rejected(self):
        client = MockLiveExchangeClient(
            submit_outcome=AdapterOutcomeStatus.ADAPTER_REJECTED,
            reject_reason="price_out_of_range",
        )
        req = AdapterSubmitRequest(
            order_id="ord_001", event_key="evt_001",
            market_id="mkt_001", side="buy", size=10.0, limit_price=0.99,
        )
        resp = client.submit_order(req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_REJECTED
        assert resp.reject_reason == "price_out_of_range"

    def test_submit_retryable_failure(self):
        client = MockLiveExchangeClient(
            submit_outcome=AdapterOutcomeStatus.ADAPTER_RETRYABLE_FAILURE,
            retryable=True,
        )
        req = AdapterSubmitRequest(
            order_id="ord_001", event_key="evt_001",
            market_id="mkt_001", side="buy", size=10.0, limit_price=0.75,
        )
        resp = client.submit_order(req)
        assert resp.retryable is True
        assert resp.terminal_failure is False

    def test_submit_terminal_failure(self):
        client = MockLiveExchangeClient(
            submit_outcome=AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE,
            terminal_failure=True,
        )
        req = AdapterSubmitRequest(
            order_id="ord_001", event_key="evt_001",
            market_id="mkt_001", side="buy", size=10.0, limit_price=0.75,
        )
        resp = client.submit_order(req)
        assert resp.terminal_failure is True

    def test_cancel_rejected(self):
        client = MockLiveExchangeClient(
            cancel_outcome=AdapterOutcomeStatus.ADAPTER_REJECTED,
            reject_reason="order_not_found",
        )
        req = AdapterCancelRequest(order_id="ord_001", event_key="evt_001")
        resp = client.cancel_order(req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_REJECTED
        assert resp.reject_reason == "order_not_found"

    def test_replace_rejected(self):
        client = MockLiveExchangeClient(
            replace_outcome=AdapterOutcomeStatus.ADAPTER_REJECTED,
            reject_reason="market_closed",
        )
        req = AdapterReplaceRequest(
            order_id="ord_001", event_key="evt_001",
            new_limit_price=0.85, new_size=20.0,
        )
        resp = client.replace_order(req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_REJECTED

    def test_get_order_update_received(self):
        client = MockLiveExchangeClient(
            update_outcome=AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED,
        )
        update = client.get_order_update("ord_001")
        assert update.outcome_status == AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED

    def test_adapter_contract_isolated_from_business_logic(self):
        """Business logic receives adapter response, not raw exchange payload."""
        client = MockLiveExchangeClient()
        req = AdapterSubmitRequest(
            order_id="ord_001", event_key="evt_001",
            market_id="mkt_001", side="buy", size=10.0, limit_price=0.75,
        )
        resp = client.submit_order(req)
        assert isinstance(resp, AdapterSubmitResponse)
        assert isinstance(resp.outcome_status, AdapterOutcomeStatus)

    def test_cancel_and_replace_are_separate_adapter_calls(self):
        """Cancel and replace never share the same adapter method."""
        client = MockLiveExchangeClient(
            cancel_outcome=AdapterOutcomeStatus.ADAPTER_ACCEPTED,
            replace_outcome=AdapterOutcomeStatus.ADAPTER_SUBMITTED,
        )
        cancel_resp = client.cancel_order(
            AdapterCancelRequest(order_id="ord_001", event_key="evt_001")
        )
        replace_resp = client.replace_order(
            AdapterReplaceRequest(
                order_id="ord_001", event_key="evt_001",
                new_limit_price=0.80, new_size=12.0,
            )
        )
        assert cancel_resp.outcome_status == AdapterOutcomeStatus.ADAPTER_ACCEPTED
        assert replace_resp.outcome_status == AdapterOutcomeStatus.ADAPTER_SUBMITTED
        assert cancel_resp.outcome_status != replace_resp.outcome_status
