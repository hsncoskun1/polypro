import pytest

from app.domain.markets.discovery import DiscoveryItem, DiscoverySummary
from app.domain.markets.registry import InMemoryMarketRegistry
from app.domain.markets.source import StubDiscoverySource, run_discovery_from_source


def make_item(market_id="mkt-001", title="Test Market", timeframe="1W"):
    return DiscoveryItem(market_id=market_id, title=title, timeframe=timeframe)


def test_empty_stub_source_returns_zero_summary():
    registry = InMemoryMarketRegistry()
    source = StubDiscoverySource([])
    summary = run_discovery_from_source(source, registry)
    assert summary == DiscoverySummary(0, 0, 0, 0)


def test_stub_source_valid_items_are_added():
    registry = InMemoryMarketRegistry()
    source = StubDiscoverySource([make_item()])
    summary = run_discovery_from_source(source, registry)
    assert summary.added_count == 1 and summary.total_seen == 1
    assert registry.get("mkt-001").market_id == "mkt-001"


def test_stub_source_duplicate_is_skipped_and_counted():
    registry = InMemoryMarketRegistry()
    source = StubDiscoverySource([make_item("mkt-001"), make_item("mkt-001")])
    summary = run_discovery_from_source(source, registry)
    assert summary.added_count == 1 and summary.skipped_duplicate_count == 1


def test_stub_source_invalid_timeframe_is_skipped_and_counted():
    registry = InMemoryMarketRegistry()
    source = StubDiscoverySource([make_item("mkt-001", timeframe="INVALID")])
    summary = run_discovery_from_source(source, registry)
    assert summary.added_count == 0 and summary.skipped_invalid_count == 1


def test_stub_source_mixed_input_produces_correct_summary():
    registry = InMemoryMarketRegistry()
    items = [
        make_item("mkt-001"),
        make_item("mkt-001"),
        make_item("mkt-002", timeframe="INVALID"),
        make_item("mkt-003"),
    ]
    source = StubDiscoverySource(items)
    summary = run_discovery_from_source(source, registry)
    assert summary.added_count == 2 and summary.skipped_duplicate_count == 1
    assert summary.skipped_invalid_count == 1 and summary.total_seen == 4
