import pytest
from app.adapters.discovery import PayloadDiscoveryAdapter, RawPayloadItem
from app.domain.markets.normalize import RawMarketItem
from app.domain.markets.registry import InMemoryMarketRegistry
from app.services.discovery import run_discovery_service


def test_adapter_empty_payload_returns_empty_list():
    adapter = PayloadDiscoveryAdapter([])
    assert adapter.fetch() == []


def test_adapter_valid_payload_returns_raw_market_items():
    payload = [RawPayloadItem(market_id="m1", title="Market One", timeframe="1W")]
    adapter = PayloadDiscoveryAdapter(payload)
    result = adapter.fetch()
    assert len(result) == 1
    assert isinstance(result[0], RawMarketItem)
    assert result[0].market_id == "m1"
    assert result[0].title == "Market One"
    assert result[0].timeframe == "1W"


def test_adapter_multiple_items_preserves_order():
    payload = [
        RawPayloadItem(market_id="a", title="A", timeframe="1D"),
        RawPayloadItem(market_id="b", title="B", timeframe="1W"),
        RawPayloadItem(market_id="c", title="C", timeframe="1M"),
    ]
    adapter = PayloadDiscoveryAdapter(payload)
    result = adapter.fetch()
    assert [r.market_id for r in result] == ["a", "b", "c"]


def test_adapter_satisfies_raw_discovery_source_contract():
    payload = [RawPayloadItem(market_id="m1", title="T", timeframe="1W")]
    adapter = PayloadDiscoveryAdapter(payload)
    items = adapter.fetch()
    assert isinstance(items, list)
    assert all(isinstance(i, RawMarketItem) for i in items)


def test_adapter_with_service_empty_payload_returns_zero_summary():
    adapter = PayloadDiscoveryAdapter([])
    registry = InMemoryMarketRegistry()
    result = run_discovery_service(adapter, registry, source_name="test")
    assert result.summary.added_count == 0
    assert result.summary.total_seen == 0


def test_adapter_with_service_valid_payload_adds_markets():
    payload = [
        RawPayloadItem(market_id="m1", title="Market One", timeframe="1W"),
        RawPayloadItem(market_id="m2", title="Market Two", timeframe="1D"),
    ]
    adapter = PayloadDiscoveryAdapter(payload)
    registry = InMemoryMarketRegistry()
    result = run_discovery_service(adapter, registry, source_name="test")
    assert result.summary.added_count == 2
    assert result.summary.total_seen == 2


def test_adapter_with_service_mixed_payload_counts_correctly():
    payload = [
        RawPayloadItem(market_id="m1", title="Valid", timeframe="1W"),
        RawPayloadItem(market_id="m1", title="Duplicate", timeframe="1W"),
        RawPayloadItem(market_id="m3", title="Bad TF", timeframe="INVALID"),
    ]
    adapter = PayloadDiscoveryAdapter(payload)
    registry = InMemoryMarketRegistry()
    result = run_discovery_service(adapter, registry, source_name="mixed")
    assert result.summary.added_count == 1
    assert result.summary.skipped_duplicate_count == 1
    assert result.summary.skipped_invalid_count == 1
    assert result.summary.total_seen == 3
