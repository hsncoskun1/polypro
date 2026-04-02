import pytest

from app.domain.markets.discovery import DiscoverySummary
from app.domain.markets.normalize import (
    NormalizationError,
    RawMarketItem,
    normalize_item,
    run_discovery_from_raw,
)
from app.domain.markets.registry import InMemoryMarketRegistry


def make_raw(market_id="mkt-001", title="Test Market", timeframe="1W"):
    return RawMarketItem(market_id=market_id, title=title, timeframe=timeframe)


def test_empty_raw_input_returns_zero_summary():
    registry = InMemoryMarketRegistry()
    summary = run_discovery_from_raw([], registry)
    assert summary == DiscoverySummary(0, 0, 0, 0)


def test_valid_raw_item_is_normalized_and_added():
    registry = InMemoryMarketRegistry()
    summary = run_discovery_from_raw([make_raw()], registry)
    assert summary.added_count == 1 and summary.total_seen == 1
    assert registry.get("mkt-001").market_id == "mkt-001"


def test_whitespace_is_stripped_during_normalization():
    registry = InMemoryMarketRegistry()
    raw = RawMarketItem(market_id="  mkt-001  ", title="  Test  ", timeframe="  1W  ")
    summary = run_discovery_from_raw([raw], registry)
    assert summary.added_count == 1
    assert registry.get("mkt-001").market_id == "mkt-001"


def test_empty_market_id_raises_normalization_error():
    with pytest.raises(NormalizationError):
        normalize_item(RawMarketItem(market_id="", title="Test", timeframe="1W"))


def test_empty_title_raises_normalization_error():
    with pytest.raises(NormalizationError):
        normalize_item(RawMarketItem(market_id="mkt-001", title="", timeframe="1W"))


def test_empty_timeframe_raises_normalization_error():
    with pytest.raises(NormalizationError):
        normalize_item(RawMarketItem(market_id="mkt-001", title="Test", timeframe=""))


def test_normalization_failure_counts_in_skipped_invalid():
    registry = InMemoryMarketRegistry()
    raw_items = [
        make_raw("mkt-001"),
        RawMarketItem(market_id="", title="Bad", timeframe="1W"),
        RawMarketItem(market_id="mkt-002", title="", timeframe="1W"),
    ]
    summary = run_discovery_from_raw(raw_items, registry)
    assert summary.added_count == 1
    assert summary.skipped_invalid_count == 2
    assert summary.total_seen == 3


def test_mixed_raw_input_produces_correct_summary():
    registry = InMemoryMarketRegistry()
    raw_items = [
        make_raw("mkt-001"),                                        # valid → added
        make_raw("mkt-001"),                                        # duplicate → skipped_duplicate
        RawMarketItem(market_id="", title="Bad", timeframe="1W"),   # empty id → skipped_invalid
        make_raw("mkt-002", timeframe="INVALID"),                   # bad timeframe → skipped_invalid
        make_raw("mkt-003"),                                        # valid → added
    ]
    summary = run_discovery_from_raw(raw_items, registry)
    assert summary.added_count == 2
    assert summary.skipped_duplicate_count == 1
    assert summary.skipped_invalid_count == 2
    assert summary.total_seen == 5
