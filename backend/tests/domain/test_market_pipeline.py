import pytest

from app.domain.markets.discovery import DiscoverySummary
from app.domain.markets.normalize import RawMarketItem
from app.domain.markets.pipeline import StubRawDiscoverySource, run_pipeline
from app.domain.markets.registry import InMemoryMarketRegistry


def make_raw(market_id="mkt-001", title="Test Market", timeframe="1W"):
    return RawMarketItem(market_id=market_id, title=title, timeframe=timeframe)


def test_empty_source_returns_zero_summary():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([])
    summary = run_pipeline(source, registry)
    assert summary == DiscoverySummary(0, 0, 0, 0)


def test_valid_source_items_are_added_via_pipeline():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([make_raw("mkt-001"), make_raw("mkt-002")])
    summary = run_pipeline(source, registry)
    assert summary.added_count == 2 and summary.total_seen == 2
    assert registry.get("mkt-001").market_id == "mkt-001"
    assert registry.get("mkt-002").market_id == "mkt-002"


def test_pipeline_counts_normalization_failures():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([
        make_raw("mkt-001"),
        RawMarketItem(market_id="", title="Bad", timeframe="1W"),
    ])
    summary = run_pipeline(source, registry)
    assert summary.added_count == 1
    assert summary.skipped_invalid_count == 1
    assert summary.total_seen == 2


def test_pipeline_counts_duplicate_items():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([make_raw("mkt-001"), make_raw("mkt-001")])
    summary = run_pipeline(source, registry)
    assert summary.added_count == 1 and summary.skipped_duplicate_count == 1


def test_pipeline_counts_invalid_timeframe():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([make_raw("mkt-001", timeframe="INVALID")])
    summary = run_pipeline(source, registry)
    assert summary.added_count == 0 and summary.skipped_invalid_count == 1


def test_source_returning_none_raises_type_error():
    class BrokenSource:
        def fetch(self):
            return None

    with pytest.raises(TypeError, match="list"):
        run_pipeline(BrokenSource(), InMemoryMarketRegistry())


def test_source_returning_non_list_raises_type_error():
    class BrokenSource:
        def fetch(self):
            return "not a list"

    with pytest.raises(TypeError, match="list"):
        run_pipeline(BrokenSource(), InMemoryMarketRegistry())


def test_total_seen_always_equals_raw_input_count():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([
        make_raw("mkt-001"),
        RawMarketItem(market_id="", title="Bad", timeframe="1W"),
        make_raw("mkt-002", timeframe="INVALID"),
        make_raw("mkt-003"),
        make_raw("mkt-003"),
    ])
    summary = run_pipeline(source, registry)
    assert summary.total_seen == 5
    assert (
        summary.added_count
        + summary.skipped_duplicate_count
        + summary.skipped_invalid_count
        == summary.total_seen
    )


def test_whitespace_only_fields_counted_as_invalid():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([
        RawMarketItem(market_id="   ", title="Test", timeframe="1W"),
        RawMarketItem(market_id="mkt-001", title="   ", timeframe="1W"),
        RawMarketItem(market_id="mkt-002", title="Test", timeframe="   "),
    ])
    summary = run_pipeline(source, registry)
    assert summary.added_count == 0
    assert summary.skipped_invalid_count == 3
    assert summary.total_seen == 3


def test_pipeline_mixed_input_produces_correct_summary():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([
        make_raw("mkt-001"),                                         # valid → added
        make_raw("mkt-001"),                                         # duplicate → skipped_duplicate
        RawMarketItem(market_id="", title="Bad", timeframe="1W"),    # empty id → skipped_invalid
        make_raw("mkt-002", timeframe="INVALID"),                    # bad timeframe → skipped_invalid
        make_raw("mkt-003"),                                         # valid → added
    ])
    summary = run_pipeline(source, registry)
    assert summary.added_count == 2
    assert summary.skipped_duplicate_count == 1
    assert summary.skipped_invalid_count == 2
    assert summary.total_seen == 5
