import pytest
from app.domain.markets.model import Market, MarketStatus, Timeframe
from app.persistence.markets import SqliteMarketStore


def make_market(market_id="mkt-001", status=MarketStatus.ACTIVE):
    return Market(market_id=market_id, title="Test Market", timeframe=Timeframe.ONE_WEEK, status=status)


# ── load ──────────────────────────────────────────────────────────────────────

def test_load_returns_empty_list_on_new_db(tmp_path):
    store = SqliteMarketStore(str(tmp_path / "markets.db"))
    assert store.load() == []


def test_load_returns_saved_markets(tmp_path):
    store = SqliteMarketStore(str(tmp_path / "markets.db"))
    market = make_market()
    store.save([market])
    loaded = store.load()
    assert len(loaded) == 1
    assert loaded[0].market_id == "mkt-001"
    assert loaded[0].title == "Test Market"
    assert loaded[0].timeframe == Timeframe.ONE_WEEK
    assert loaded[0].status == MarketStatus.ACTIVE


def test_load_preserves_inactive_status(tmp_path):
    store = SqliteMarketStore(str(tmp_path / "markets.db"))
    market = make_market(status=MarketStatus.INACTIVE)
    store.save([market])
    loaded = store.load()
    assert loaded[0].status == MarketStatus.INACTIVE


def test_load_preserves_multiple_markets(tmp_path):
    store = SqliteMarketStore(str(tmp_path / "markets.db"))
    markets = [make_market("mkt-001"), make_market("mkt-002"), make_market("mkt-003")]
    store.save(markets)
    loaded = store.load()
    assert len(loaded) == 3
    ids = {m.market_id for m in loaded}
    assert ids == {"mkt-001", "mkt-002", "mkt-003"}


# ── save ──────────────────────────────────────────────────────────────────────

def test_save_creates_parent_directories(tmp_path):
    store = SqliteMarketStore(str(tmp_path / "subdir" / "markets.db"))
    store.save([make_market()])
    assert (tmp_path / "subdir" / "markets.db").exists()


def test_save_overwrites_previous_data(tmp_path):
    store = SqliteMarketStore(str(tmp_path / "markets.db"))
    store.save([make_market("mkt-001")])
    store.save([make_market("mkt-002")])
    loaded = store.load()
    assert len(loaded) == 1
    assert loaded[0].market_id == "mkt-002"


def test_save_empty_list_clears_store(tmp_path):
    store = SqliteMarketStore(str(tmp_path / "markets.db"))
    store.save([make_market()])
    store.save([])
    assert store.load() == []
