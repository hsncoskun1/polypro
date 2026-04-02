import pytest
from app.domain.markets.discovery import DiscoveryItem, DiscoverySummary, run_discovery
from app.domain.markets.registry import InMemoryMarketRegistry


def make_item(market_id="mkt-001", title="Test Market", timeframe="1W"):
    return DiscoveryItem(market_id=market_id, title=title, timeframe=timeframe)


def test_empty_input_returns_zero_summary():
    registry = InMemoryMarketRegistry()
    summary = run_discovery([], registry)
    assert summary == DiscoverySummary(
        added_count=0,
        skipped_duplicate_count=0,
        skipped_invalid_count=0,
        total_seen=0,
    )


def test_valid_market_is_added_to_registry():
    registry = InMemoryMarketRegistry()
    summary = run_discovery([make_item()], registry)
    assert summary.added_count == 1
    assert summary.total_seen == 1
    assert registry.get("mkt-001").market_id == "mkt-001"


def test_duplicate_market_is_skipped_and_counted():
    registry = InMemoryMarketRegistry()
    items = [make_item("mkt-001"), make_item("mkt-001")]
    summary = run_discovery(items, registry)
    assert summary.added_count == 1
    assert summary.skipped_duplicate_count == 1
    assert summary.total_seen == 2


def test_invalid_timeframe_is_skipped_and_counted():
    registry = InMemoryMarketRegistry()
    items = [make_item("mkt-001", timeframe="INVALID")]
    summary = run_discovery(items, registry)
    assert summary.added_count == 0
    assert summary.skipped_invalid_count == 1
    assert summary.total_seen == 1


def test_mixed_input_produces_correct_summary():
    registry = InMemoryMarketRegistry()
    items = [
        make_item("mkt-001"),                       # valid
        make_item("mkt-001"),                       # duplicate
        make_item("mkt-002", timeframe="INVALID"),  # invalid timeframe
        make_item("mkt-003"),                       # valid
    ]
    summary = run_discovery(items, registry)
    assert summary.added_count == 2
    assert summary.skipped_duplicate_count == 1
    assert summary.skipped_invalid_count == 1
    assert summary.total_seen == 4
