from app.domain.markets.model import Market, MarketStatus, Timeframe
from app.domain.markets.exceptions import (
    DuplicateMarketError,
    MarketNotFoundError,
    InvalidTimeframeError,
)


def parse_timeframe(value: str) -> Timeframe:
    """Parse a timeframe string, raising InvalidTimeframeError if unsupported."""
    try:
        return Timeframe(value)
    except ValueError:
        raise InvalidTimeframeError(value)


class InMemoryMarketRegistry:
    """In-memory market registry. Single source of truth for market domain state."""

    def __init__(self) -> None:
        self._markets: dict[str, Market] = {}

    def add(self, market: Market) -> None:
        """Register a new market. Raises DuplicateMarketError if ID already exists."""
        if market.market_id in self._markets:
            raise DuplicateMarketError(market.market_id)
        self._markets[market.market_id] = market

    def get(self, market_id: str) -> Market:
        """Retrieve a market by ID. Raises MarketNotFoundError if not found."""
        if market_id not in self._markets:
            raise MarketNotFoundError(market_id)
        return self._markets[market_id]

    def list(self, active_only: bool = False) -> list[Market]:
        """Return all markets, optionally filtered to active only."""
        markets = list(self._markets.values())
        if active_only:
            markets = [m for m in markets if m.status == MarketStatus.ACTIVE]
        return markets

    def update_status(self, market_id: str, status: MarketStatus) -> None:
        """Update a market's status. Raises MarketNotFoundError if not found."""
        market = self.get(market_id)
        market.status = status
