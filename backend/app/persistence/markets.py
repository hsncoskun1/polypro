import json
import pathlib

from app.domain.markets.model import Market, MarketStatus, Timeframe


class JsonMarketStore:
    """Persists market registry state to a JSON file."""

    def __init__(self, path: str) -> None:
        self._path = pathlib.Path(path)

    def load(self) -> list[Market]:
        if not self._path.exists():
            return []
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return [
            Market(
                market_id=d["market_id"],
                title=d["title"],
                timeframe=Timeframe(d["timeframe"]),
                status=MarketStatus(d["status"]),
            )
            for d in data
        ]

    def save(self, markets: list[Market]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "market_id": m.market_id,
                "title": m.title,
                "timeframe": m.timeframe.value,
                "status": m.status.value,
            }
            for m in markets
        ]
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")
