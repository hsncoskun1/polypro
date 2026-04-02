from dataclasses import dataclass

from app.domain.markets.normalize import RawMarketItem


@dataclass
class RawPayloadItem:
    """Raw external payload format — placeholder for future Polymarket API response fields."""

    market_id: str
    title: str
    timeframe: str


class PayloadDiscoveryAdapter:
    """Adapts a list of raw payload items to the RawDiscoverySource contract.

    Seam point for future external source integration. Currently maps
    RawPayloadItem objects directly to RawMarketItem. When a real HTTP
    source is added, only this class changes — pipeline, service, and
    API layers remain untouched.
    """

    def __init__(self, payload: list[RawPayloadItem]) -> None:
        self._payload = payload

    def fetch(self) -> list[RawMarketItem]:
        return [
            RawMarketItem(
                market_id=item.market_id,
                title=item.title,
                timeframe=item.timeframe,
            )
            for item in self._payload
        ]
