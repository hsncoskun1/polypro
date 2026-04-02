"""Position lifecycle persistence — SQLite-backed store for persisted positions.

Design decisions:
- Follows the same SQLite pattern as SqliteMarketStore.
- open_position() inserts a new OPEN position record.
- close_position() transitions an existing position to CLOSED, setting exit_reason
  and closed_at. Does not delete records — closed positions remain for audit.
- load_open_positions() returns only OPEN positions, used for restart recovery.
- restore_locks_from_positions() derives the set of locked event_keys from a list
  of open positions, used to restore ExecutionLock state after restart.
- Closed positions are never returned by load_open_positions() — they do not
  pollute the active position set.
- PnL calculation, balance accounting, and claim lifecycle are NOT in scope.
- Runtime state is never edited directly through this store.
"""
import sqlite3
import pathlib
from typing import Optional

from app.domain.position.persisted_position import PersistedPosition
from app.domain.position.position_state import PositionState


class SqlitePositionStore:
    """SQLite-backed store for position lifecycle persistence."""

    def __init__(self, path: str) -> None:
        self._path = pathlib.Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    position_id            TEXT PRIMARY KEY,
                    event_key              TEXT NOT NULL,
                    side                   TEXT NOT NULL,
                    status                 TEXT NOT NULL,
                    trigger_price          REAL NOT NULL,
                    order_submitted_price  REAL NOT NULL,
                    fill_price             REAL NOT NULL,
                    trigger_move_value     REAL NOT NULL,
                    fill_move_value        REAL NOT NULL,
                    requested_size         REAL NOT NULL,
                    filled_size            REAL NOT NULL,
                    entry_reason           TEXT NOT NULL,
                    exit_reason            TEXT NOT NULL,
                    opened_at              TEXT NOT NULL,
                    closed_at              TEXT
                )
                """
            )

    def open_position(self, position: PersistedPosition) -> None:
        """Insert a new OPEN position record.

        Args:
            position: The position to persist. Must have status=OPEN.
        """
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                INSERT INTO positions (
                    position_id, event_key, side, status,
                    trigger_price, order_submitted_price, fill_price,
                    trigger_move_value, fill_move_value,
                    requested_size, filled_size,
                    entry_reason, exit_reason,
                    opened_at, closed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    position.position_id,
                    position.event_key,
                    position.side,
                    position.status.value,
                    position.trigger_price,
                    position.order_submitted_price,
                    position.fill_price,
                    position.trigger_move_value,
                    position.fill_move_value,
                    position.requested_size,
                    position.filled_size,
                    position.entry_reason,
                    position.exit_reason,
                    position.opened_at,
                    position.closed_at,
                ),
            )

    def close_position(
        self,
        position_id: str,
        exit_reason: str,
        closed_at: str,
    ) -> None:
        """Transition an existing position to CLOSED.

        Updates status, exit_reason, and closed_at. Does not delete the record.

        Args:
            position_id: ID of the position to close.
            exit_reason: Reason the position was exited.
            closed_at: ISO 8601 UTC timestamp of close.
        """
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                UPDATE positions
                SET status = ?, exit_reason = ?, closed_at = ?
                WHERE position_id = ?
                """,
                (PositionState.CLOSED.value, exit_reason, closed_at, position_id),
            )

    def load_open_positions(self) -> list[PersistedPosition]:
        """Return all positions with status=OPEN.

        Used for restart recovery. Closed positions are excluded.

        Returns:
            List of PersistedPosition with status=OPEN.
        """
        with sqlite3.connect(self._path) as conn:
            rows = conn.execute(
                """
                SELECT position_id, event_key, side, status,
                       trigger_price, order_submitted_price, fill_price,
                       trigger_move_value, fill_move_value,
                       requested_size, filled_size,
                       entry_reason, exit_reason,
                       opened_at, closed_at
                FROM positions
                WHERE status = ?
                """,
                (PositionState.OPEN.value,),
            ).fetchall()
        return [_row_to_position(row) for row in rows]

    def load_all_positions(self) -> list[PersistedPosition]:
        """Return all positions (OPEN and CLOSED).

        Used for audit and testing purposes.

        Returns:
            List of all PersistedPosition records.
        """
        with sqlite3.connect(self._path) as conn:
            rows = conn.execute(
                """
                SELECT position_id, event_key, side, status,
                       trigger_price, order_submitted_price, fill_price,
                       trigger_move_value, fill_move_value,
                       requested_size, filled_size,
                       entry_reason, exit_reason,
                       opened_at, closed_at
                FROM positions
                """,
            ).fetchall()
        return [_row_to_position(row) for row in rows]


def restore_locks_from_positions(
    positions: list[PersistedPosition],
) -> set[str]:
    """Derive the set of locked event_keys from a list of open positions.

    Used after restart to restore ExecutionLock state. Each open position
    holds a lock on its event_key to prevent duplicate entries.

    Args:
        positions: List of open PersistedPosition records.

    Returns:
        Set of event_key strings that should be locked.
    """
    return {p.event_key for p in positions}


def _row_to_position(row: tuple) -> PersistedPosition:
    """Convert a DB row tuple to a PersistedPosition."""
    return PersistedPosition(
        position_id=row[0],
        event_key=row[1],
        side=row[2],
        status=PositionState(row[3]),
        trigger_price=row[4],
        order_submitted_price=row[5],
        fill_price=row[6],
        trigger_move_value=row[7],
        fill_move_value=row[8],
        requested_size=row[9],
        filled_size=row[10],
        entry_reason=row[11],
        exit_reason=row[12],
        opened_at=row[13],
        closed_at=row[14],
    )
