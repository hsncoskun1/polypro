import sqlite3
import pathlib

from app.domain.markets.model import Market, MarketStatus, Timeframe


class SqliteMarketStore:
    """Persists market registry state to a SQLite database."""

    def __init__(self, path: str) -> None:
        self._path = pathlib.Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS markets (
                    market_id TEXT PRIMARY KEY,
                    title     TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    status    TEXT NOT NULL
                )
                """
            )

    def load(self) -> list[Market]:
        with sqlite3.connect(self._path) as conn:
            rows = conn.execute(
                "SELECT market_id, title, timeframe, status FROM markets"
            ).fetchall()
        markets = []
        for row in rows:
            try:
                markets.append(
                    Market(
                        market_id=row[0],
                        title=row[1],
                        timeframe=Timeframe(row[2]),
                        status=MarketStatus(row[3]),
                    )
                )
            except ValueError as exc:
                raise ValueError(
                    f"Corrupt market row in DB (market_id={row[0]!r}): {exc}"
                ) from exc
        return markets

    def save(self, markets: list[Market]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._path) as conn:
            conn.execute("DELETE FROM markets")
            conn.executemany(
                "INSERT INTO markets (market_id, title, timeframe, status) VALUES (?, ?, ?, ?)",
                [
                    (m.market_id, m.title, m.timeframe.value, m.status.value)
                    for m in markets
                ],
            )
