from datetime import UTC, datetime

import pytest

from app.domain.markets.discovery import DiscoverySummary
from app.domain.markets.normalize import RawMarketItem
from app.domain.markets.pipeline import StubRawDiscoverySource
from app.domain.markets.registry import InMemoryMarketRegistry
from app.services.discovery import DiscoveryResult, run_discovery_service


def make_raw(market_id="mkt-001", title="Test Market", timeframe="1W"):
    return RawMarketItem(market_id=market_id, title=title, timeframe=timeframe)


def test_service_empty_source_returns_zero_summary():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([])
    result = run_discovery_service(source, registry)
    assert result.summary == DiscoverySummary(0, 0, 0, 0)


def test_service_valid_source_returns_correct_summary():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([make_raw("mkt-001"), make_raw("mkt-002")])
    result = run_discovery_service(source, registry)
    assert result.summary.added_count == 2 and result.summary.total_seen == 2


def test_service_mixed_source_returns_correct_summary():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([
        make_raw("mkt-001"),
        make_raw("mkt-001"),
        RawMarketItem(market_id="", title="Bad", timeframe="1W"),
        make_raw("mkt-002", timeframe="INVALID"),
        make_raw("mkt-003"),
    ])
    result = run_discovery_service(source, registry)
    assert result.summary.added_count == 2
    assert result.summary.skipped_duplicate_count == 1
    assert result.summary.skipped_invalid_count == 2
    assert result.summary.total_seen == 5


def test_service_source_name_is_included_in_result():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([])
    result = run_discovery_service(source, registry, source_name="stub-v1")
    assert result.source_name == "stub-v1"


def test_service_default_source_name_is_unknown():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([])
    result = run_discovery_service(source, registry)
    assert result.source_name == "unknown"


def test_service_ran_at_is_set_and_timezone_aware():
    registry = InMemoryMarketRegistry()
    source = StubRawDiscoverySource([])
    before = datetime.now(UTC)
    result = run_discovery_service(source, registry)
    after = datetime.now(UTC)
    assert before <= result.ran_at <= after
    assert result.ran_at.tzinfo is not None
