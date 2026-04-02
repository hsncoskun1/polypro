from unittest.mock import MagicMock, patch

import pytest

from app.clients.polymarket import PolymarketClientError
from app.clients.polymarket_mapping import ClientPayloadMappingError
from app.clients.timeframe_mapping import TimeframeMappingError
from app.domain.markets.registry import InMemoryMarketRegistry
from app.services.discovery_client import (
    run_polymarket_client_discovery,
    run_polymarket_fetch_to_discovery,
)

URL = "https://example.com/markets"

# Far-future date — always maps to 3M, stable across test runs.
FAR_FUTURE = "2099-12-31"


def _registry():
    return InMemoryMarketRegistry()


def _valid_row(condition_id="cid1", question="Q?", end_date=FAR_FUTURE):
    return {"condition_id": condition_id, "question": question, "end_date": end_date}


def _mock_client(*rows):
    """Return a MagicMock PolymarketClient whose fetch() returns the given rows."""
    client = MagicMock()
    client.fetch.return_value = list(rows)
    return client


# ── run_polymarket_fetch_to_discovery (client injection) ────────────────────

class TestRunPolymarketFetchToDiscovery:
    def test_valid_rows_return_discovery_result_with_added_count(self):
        client = _mock_client(_valid_row("cid1"), _valid_row("cid2"))
        result = run_polymarket_fetch_to_discovery(client, _registry())
        assert result.summary.added_count == 2
        assert result.summary.total_seen == 2

    def test_duplicate_rows_reflected_in_summary(self):
        client = _mock_client(_valid_row("cid1"), _valid_row("cid1"))
        result = run_polymarket_fetch_to_discovery(client, _registry())
        assert result.summary.added_count == 1
        assert result.summary.skipped_duplicate_count == 1
        assert result.summary.total_seen == 2

    def test_empty_fetch_returns_zero_summary(self):
        client = _mock_client()
        result = run_polymarket_fetch_to_discovery(client, _registry())
        assert result.summary.added_count == 0
        assert result.summary.total_seen == 0

    def test_client_error_propagates(self):
        client = MagicMock()
        client.fetch.side_effect = PolymarketClientError("timeout")
        with pytest.raises(PolymarketClientError, match="timeout"):
            run_polymarket_fetch_to_discovery(client, _registry())

    def test_missing_key_raises_client_payload_mapping_error(self):
        client = _mock_client({"question": "Q?", "end_date": FAR_FUTURE})  # no condition_id
        with pytest.raises(ClientPayloadMappingError):
            run_polymarket_fetch_to_discovery(client, _registry())

    def test_past_end_date_raises_timeframe_mapping_error(self):
        client = _mock_client(_valid_row(end_date="2020-01-01"))
        with pytest.raises(TimeframeMappingError, match="in the past"):
            run_polymarket_fetch_to_discovery(client, _registry())

    def test_unparseable_end_date_raises_timeframe_mapping_error(self):
        client = _mock_client(_valid_row(end_date="not-a-date"))
        with pytest.raises(TimeframeMappingError, match="Cannot parse"):
            run_polymarket_fetch_to_discovery(client, _registry())

    def test_result_carries_source_name(self):
        client = _mock_client(_valid_row())
        result = run_polymarket_fetch_to_discovery(client, _registry(), source_name="poly-test")
        assert result.source_name == "poly-test"

    def test_result_has_ran_at(self):
        client = _mock_client(_valid_row())
        result = run_polymarket_fetch_to_discovery(client, _registry())
        assert result.ran_at is not None
        assert result.ran_at.tzinfo is not None


# ── run_polymarket_client_discovery (URL wrapper) ────────────────────────────

class TestRunPolymarketClientDiscovery:
    def test_valid_rows_return_discovery_result_with_added_count(self):
        rows = [_valid_row("cid1"), _valid_row("cid2")]
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = rows
            result = run_polymarket_client_discovery(URL, _registry())
        assert result.summary.added_count == 2
        assert result.summary.total_seen == 2

    def test_duplicate_rows_reflected_in_summary(self):
        rows = [_valid_row("cid1"), _valid_row("cid1")]
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = rows
            result = run_polymarket_client_discovery(URL, _registry())
        assert result.summary.added_count == 1
        assert result.summary.skipped_duplicate_count == 1
        assert result.summary.total_seen == 2

    def test_mixed_valid_and_invalid_rows_missing_key_raises(self):
        rows = [_valid_row("cid1"), {"question": "Q?", "end_date": FAR_FUTURE}]
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = rows
            with pytest.raises(ClientPayloadMappingError):
                run_polymarket_client_discovery(URL, _registry())

    def test_empty_rows_return_zero_summary(self):
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = []
            result = run_polymarket_client_discovery(URL, _registry())
        assert result.summary.added_count == 0
        assert result.summary.total_seen == 0

    def test_client_error_propagates(self):
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.side_effect = PolymarketClientError("timeout")
            with pytest.raises(PolymarketClientError, match="timeout"):
                run_polymarket_client_discovery(URL, _registry())

    def test_past_end_date_raises_timeframe_mapping_error(self):
        rows = [_valid_row(end_date="2020-01-01")]
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = rows
            with pytest.raises(TimeframeMappingError, match="in the past"):
                run_polymarket_client_discovery(URL, _registry())

    def test_unparseable_end_date_raises_timeframe_mapping_error(self):
        rows = [_valid_row(end_date="not-a-date")]
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = rows
            with pytest.raises(TimeframeMappingError, match="Cannot parse"):
                run_polymarket_client_discovery(URL, _registry())
