class DuplicateMarketError(Exception):
    """Raised when a market with the same ID already exists in the registry."""
    def __init__(self, market_id: str) -> None:
        super().__init__(f"Market already exists: {market_id}")
        self.market_id = market_id


class MarketNotFoundError(Exception):
    """Raised when a requested market does not exist in the registry."""
    def __init__(self, market_id: str) -> None:
        super().__init__(f"Market not found: {market_id}")
        self.market_id = market_id


class InvalidTimeframeError(Exception):
    """Raised when an unsupported timeframe value is provided."""
    def __init__(self, value: str) -> None:
        super().__init__(f"Invalid timeframe: '{value}'. Supported: 1D, 1W, 1M, 3M")
        self.value = value
