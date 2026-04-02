from unittest.mock import MagicMock, patch

import pytest

from app.clients.polymarket import PolymarketClientError
from app.clients.polymarket_mapping import ClientPayloadMappingError
from app.domain.markets.registry import InMemoryMarketRegistry
from app.services.discovery_client import run_polymarket_client_discovery

URL = "https://example.com/markets"


def _registry():
    return InMemoryMarketRegistry()


def _rows(*items):
    return list(items)


def _valid_row(condition_id="cid1", question="Q?", end_date="1W"):
    return {"condition_id": condition_id, "question": question, "end_date": end_date}


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
        rows = [_valid_row("cid1"), {"question": "Q?", "end_date": "1W"}]  # condition_id key missing
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = rows
            # missing condition_id key → ClientPayloadMappingError propagates
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

    def test_result_carries_source_name(self):
        rows = [_valid_row()]
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = rows
            result = run_polymarket_client_discovery(URL, _registry(), source_name="poly-test")
        assert result.source_name == "poly-test"

    def test_result_has_ran_at(self):
        rows = [_valid_row()]
        with patch("app.services.discovery_client.PolymarketClient") as MockClient:
            MockClient.return_value.fetch.return_value = rows
            result = run_polymarket_client_discovery(URL, _registry())
        assert result.ran_at is not None
        assert result.ran_at.tzinfo is not None
