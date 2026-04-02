import pytest
from app.domain.markets.model import Market, MarketStatus, Timeframe
from app.domain.markets.registry import InMemoryMarketRegistry, parse_timeframe
from app.domain.markets.exceptions import (
    DuplicateMarketError,
    MarketNotFoundError,
    InvalidTimeframeError,
)


def make_market(market_id="mkt-001", title="Test Market", timeframe=Timeframe.ONE_WEEK):
    return Market(market_id=market_id, title=title, timeframe=timeframe)


# ── parse_timeframe ───────────────────────────────────────────────────────────

def test_parse_timeframe_valid():
    assert parse_timeframe("1D") == Timeframe.ONE_DAY
    assert parse_timeframe("1W") == Timeframe.ONE_WEEK
    assert parse_timeframe("1M") == Timeframe.ONE_MONTH
    assert parse_timeframe("3M") == Timeframe.THREE_MONTHS


def test_parse_timeframe_invalid():
    with pytest.raises(InvalidTimeframeError) as exc_info:
        parse_timeframe("INVALID")
    assert "INVALID" in str(exc_info.value)


# ── list ──────────────────────────────────────────────────────────────────────

def test_empty_registry_returns_empty_list():
    registry = InMemoryMarketRegistry()
    assert registry.list() == []


# ── add ───────────────────────────────────────────────────────────────────────

def test_add_valid_market():
    registry = InMemoryMarketRegistry()
    market = make_market()
    registry.add(market)
    assert len(registry.list()) == 1


def test_add_duplicate_market_raises():
    registry = InMemoryMarketRegistry()
    market = make_market()
    registry.add(market)
    with pytest.raises(DuplicateMarketError) as exc_info:
        registry.add(make_market())
    assert "mkt-001" in str(exc_info.value)


# ── get ───────────────────────────────────────────────────────────────────────

def test_get_added_market():
    registry = InMemoryMarketRegistry()
    market = make_market()
    registry.add(market)
    result = registry.get("mkt-001")
    assert result.title == "Test Market"
    assert result.timeframe == Timeframe.ONE_WEEK


def test_get_missing_market_raises():
    registry = InMemoryMarketRegistry()
    with pytest.raises(MarketNotFoundError) as exc_info:
        registry.get("nonexistent")
    assert "nonexistent" in str(exc_info.value)


# ── list active_only ──────────────────────────────────────────────────────────

def test_list_active_only_filter():
    registry = InMemoryMarketRegistry()
    registry.add(make_market("mkt-001"))
    registry.add(make_market("mkt-002"))
    registry.update_status("mkt-002", MarketStatus.INACTIVE)
    active = registry.list(active_only=True)
    assert len(active) == 1
    assert active[0].market_id == "mkt-001"


# ── update_status ─────────────────────────────────────────────────────────────

def test_update_status_changes_market_status():
    registry = InMemoryMarketRegistry()
    registry.add(make_market())
    registry.update_status("mkt-001", MarketStatus.INACTIVE)
    assert registry.get("mkt-001").status == MarketStatus.INACTIVE


def test_update_status_missing_market_raises():
    registry = InMemoryMarketRegistry()
    with pytest.raises(MarketNotFoundError):
        registry.update_status("nonexistent", MarketStatus.INACTIVE)
