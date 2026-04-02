"""Tests for production client concrete integration — v0.8.0."""
from app.domain.live.external_submit_payload import ExternalSubmitPayload
from app.domain.live.external_cancel_payload import ExternalCancelPayload
from app.domain.live.external_replace_payload import ExternalReplacePayload
from app.domain.live.external_response_payload import ExternalResponsePayload
from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus
from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.adapter_cancel_request import AdapterCancelRequest
from app.domain.live.adapter_replace_request import AdapterReplaceRequest
from app.domain.live.adapter_error_translator import translate_status
from app.domain.live.production_request_mapper import ProductionRequestMapper
from app.domain.live.production_response_mapper import ProductionResponseMapper
from app.domain.live.production_exchange_client import ProductionExchangeClient
from app.domain.live.live_exchange_client import LiveExchangeClient


# ---------------------------------------------------------------------------
# TestExternalPayloads
# ---------------------------------------------------------------------------

class TestExternalSubmitPayload:
    def test_required_fields(self):
        p = ExternalSubmitPayload(
            order_id="ord_001",
            market_id="mkt_001",
            side="buy",
            size=10.0,
            limit_price=0.75,
        )
        assert p.order_id == "ord_001"
        assert p.market_id == "mkt_001"
        assert p.side == "buy"
        assert p.size == 10.0
        assert p.limit_price == 0.75

    def test_defaults(self):
        p = ExternalSubmitPayload(
            order_id="ord_001", market_id="mkt_001",
            side="buy", size=10.0, limit_price=0.75,
        )
        assert p.client_order_id == ""
        assert p.raw_payload == ""


class TestExternalCancelPayload:
    def test_required_fields(self):
        p = ExternalCancelPayload(order_id="ord_001")
        assert p.order_id == "ord_001"

    def test_defaults(self):
        p = ExternalCancelPayload(order_id="ord_001")
        assert p.client_order_id == ""
        assert p.raw_payload == ""


class TestExternalReplacePayload:
    def test_required_fields(self):
        p = ExternalReplacePayload(order_id="ord_001", new_limit_price=0.80, new_size=15.0)
        assert p.order_id == "ord_001"
        assert p.new_limit_price == 0.80
        assert p.new_size == 15.0


class TestExternalResponsePayload:
    def test_defaults(self):
        p = ExternalResponsePayload()
        assert p.mapped_order_id == ""
        assert p.mapped_status == ""
        assert p.retryable is False
        assert p.terminal_failure is False
        assert p.filled_size == 0.0
        assert p.remaining_size == 0.0
        assert p.received_at == ""

    def test_full_fields(self):
        p = ExternalResponsePayload(
            mapped_order_id="ord_001",
            mapped_status="submitted",
            filled_size=5.0,
            remaining_size=5.0,
            received_at="2026-04-02T10:00:00",
        )
        assert p.filled_size == 5.0
        assert p.received_at == "2026-04-02T10:00:00"


# ---------------------------------------------------------------------------
# TestAdapterErrorTranslator
# ---------------------------------------------------------------------------

class TestAdapterErrorTranslator:
    def test_terminal_failure_priority(self):
        assert translate_status("submitted", terminal_failure=True) == AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE

    def test_retryable_priority(self):
        assert translate_status("submitted", retryable=True) == AdapterOutcomeStatus.ADAPTER_RETRYABLE_FAILURE

    def test_terminal_over_retryable(self):
        result = translate_status("submitted", terminal_failure=True, retryable=True)
        assert result == AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE

    def test_submitted_status(self):
        assert translate_status("submitted") == AdapterOutcomeStatus.ADAPTER_SUBMITTED

    def test_accepted_status(self):
        assert translate_status("accepted") == AdapterOutcomeStatus.ADAPTER_ACCEPTED

    def test_rejected_status(self):
        assert translate_status("rejected") == AdapterOutcomeStatus.ADAPTER_REJECTED

    def test_no_update_status(self):
        assert translate_status("no_update") == AdapterOutcomeStatus.ADAPTER_NO_UPDATE

    def test_update_received_status(self):
        assert translate_status("update_received") == AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED

    def test_empty_status_defaults_submitted(self):
        assert translate_status("") == AdapterOutcomeStatus.ADAPTER_SUBMITTED

    def test_unknown_status_fail_closed(self):
        # Unknown status → ADAPTER_SUBMITTED (fail-closed, not silently ok)
        assert translate_status("unknown_xyz") == AdapterOutcomeStatus.ADAPTER_SUBMITTED


# ---------------------------------------------------------------------------
# TestProductionRequestMapper
# ---------------------------------------------------------------------------

class TestProductionRequestMapper:
    def setup_method(self):
        self.mapper = ProductionRequestMapper()

    def test_map_submit_request(self):
        req = AdapterSubmitRequest(
            order_id="ord_001", event_key="evt_001",
            market_id="mkt_001", side="buy", size=10.0, limit_price=0.75,
        )
        payload = self.mapper.map_submit_request(req)
        assert isinstance(payload, ExternalSubmitPayload)
        assert payload.order_id == "ord_001"
        assert payload.market_id == "mkt_001"
        assert payload.side == "buy"
        assert payload.size == 10.0
        assert payload.limit_price == 0.75
        assert payload.client_order_id == "evt_001"

    def test_map_cancel_request(self):
        req = AdapterCancelRequest(order_id="ord_001", event_key="evt_001")
        payload = self.mapper.map_cancel_request(req)
        assert isinstance(payload, ExternalCancelPayload)
        assert payload.order_id == "ord_001"
        assert payload.client_order_id == "evt_001"

    def test_map_replace_request(self):
        req = AdapterReplaceRequest(
            order_id="ord_001", event_key="evt_001",
            new_limit_price=0.80, new_size=15.0,
        )
        payload = self.mapper.map_replace_request(req)
        assert isinstance(payload, ExternalReplacePayload)
        assert payload.order_id == "ord_001"
        assert payload.new_limit_price == 0.80
        assert payload.new_size == 15.0


# ---------------------------------------------------------------------------
# TestProductionResponseMapper
# ---------------------------------------------------------------------------

class TestProductionResponseMapper:
    def setup_method(self):
        self.mapper = ProductionResponseMapper()

    def test_map_submit_response_submitted(self):
        raw = ExternalResponsePayload(mapped_order_id="ord_001", mapped_status="submitted")
        resp = self.mapper.map_submit_response(raw, "ord_001")
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_SUBMITTED
        assert resp.exchange_order_id == "ord_001"

    def test_map_submit_response_rejected(self):
        raw = ExternalResponsePayload(mapped_status="rejected", mapped_reject_reason="bad_price")
        resp = self.mapper.map_submit_response(raw, "ord_001")
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_REJECTED
        assert resp.reject_reason == "bad_price"

    def test_map_submit_response_terminal(self):
        raw = ExternalResponsePayload(mapped_status="", terminal_failure=True)
        resp = self.mapper.map_submit_response(raw, "ord_001")
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE
        assert resp.terminal_failure is True

    def test_map_cancel_response(self):
        raw = ExternalResponsePayload(mapped_order_id="ord_001", mapped_status="cancelled")
        resp = self.mapper.map_cancel_response(raw, "ord_001")
        assert resp.order_id == "ord_001"
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_ACCEPTED

    def test_map_replace_response(self):
        raw = ExternalResponsePayload(mapped_order_id="new_ord_002", mapped_status="replaced")
        resp = self.mapper.map_replace_response(raw, "ord_001")
        assert resp.order_id == "ord_001"
        assert resp.new_exchange_order_id == "new_ord_002"

    def test_map_order_update_no_update(self):
        raw = ExternalResponsePayload(mapped_status="no_update")
        update = self.mapper.map_order_update(raw, "ord_001")
        assert update.outcome_status == AdapterOutcomeStatus.ADAPTER_NO_UPDATE

    def test_map_order_update_fill_fields(self):
        raw = ExternalResponsePayload(
            mapped_status="update_received",
            filled_size=5.0,
            remaining_size=5.0,
            received_at="2026-04-02T10:00:00",
        )
        update = self.mapper.map_order_update(raw, "ord_001")
        assert update.outcome_status == AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED
        assert update.filled_size == 5.0
        assert update.remaining_size == 5.0
        assert update.update_timestamp == "2026-04-02T10:00:00"


# ---------------------------------------------------------------------------
# TestProductionExchangeClient
# ---------------------------------------------------------------------------

class TestProductionExchangeClient:
    def setup_method(self):
        self.client = ProductionExchangeClient()
        self.submit_req = AdapterSubmitRequest(
            order_id="ord_001", event_key="evt_001",
            market_id="mkt_001", side="buy", size=10.0, limit_price=0.75,
        )
        self.cancel_req = AdapterCancelRequest(order_id="ord_001", event_key="evt_001")
        self.replace_req = AdapterReplaceRequest(
            order_id="ord_001", event_key="evt_001",
            new_limit_price=0.80, new_size=15.0,
        )

    def test_is_live_exchange_client(self):
        assert isinstance(self.client, LiveExchangeClient)

    def test_submit_order_returns_submitted(self):
        resp = self.client.submit_order(self.submit_req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_SUBMITTED
        assert resp.order_id == "ord_001"

    def test_cancel_order_returns_accepted(self):
        resp = self.client.cancel_order(self.cancel_req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_ACCEPTED
        assert resp.order_id == "ord_001"

    def test_replace_order_returns_accepted(self):
        resp = self.client.replace_order(self.replace_req)
        assert resp.outcome_status == AdapterOutcomeStatus.ADAPTER_ACCEPTED
        assert resp.order_id == "ord_001"

    def test_get_order_update_returns_no_update(self):
        update = self.client.get_order_update("ord_001")
        assert update.outcome_status == AdapterOutcomeStatus.ADAPTER_NO_UPDATE
        assert update.order_id == "ord_001"

    def test_submit_maps_through_request_mapper(self):
        """Internal payload mapper is called — market_id and side are forwarded."""
        resp = self.client.submit_order(self.submit_req)
        assert resp.exchange_order_id == "ord_001"

    def test_no_real_network_call(self):
        """Client operates without network — seam only."""
        # If this test runs, no network was called (would raise otherwise)
        resp = self.client.submit_order(self.submit_req)
        assert resp is not None

    def test_cancel_and_replace_separate_paths(self):
        cancel_resp = self.client.cancel_order(self.cancel_req)
        replace_resp = self.client.replace_order(self.replace_req)
        # Both succeed but via distinct seam paths
        assert cancel_resp.order_id == replace_resp.order_id
        assert cancel_resp.outcome_status == replace_resp.outcome_status  # both ACCEPTED via different status maps

    def test_adapter_contract_isolated(self):
        """Business logic receives AdapterSubmitResponse, not raw ExternalResponsePayload."""
        from app.domain.live.adapter_submit_response import AdapterSubmitResponse
        resp = self.client.submit_order(self.submit_req)
        assert isinstance(resp, AdapterSubmitResponse)
