"""Persisted position model — full snapshot of a position lifecycle record.

Design decisions:
- trigger, order_submitted, and fill are distinct moments with separate price fields.
  These must not be collapsed — they represent different points in the execution chain.
- trigger_move_value and fill_move_value capture the adverse/favorable move at each
  moment relative to entry; PnL authoritative calculation is NOT in scope here.
- requested_size and filled_size are stored separately to reflect partial fills.
- entry_reason and exit_reason provide full auditability of why positions were opened
  and closed.
- closed_at is Optional — only set when status transitions to CLOSED.
- All timestamps are ISO 8601 strings (UTC).
- Runtime state is never edited directly; persistence helpers manage transitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.domain.position.position_state import PositionState


@dataclass
class PersistedPosition:
    """Full snapshot record for a position across its lifecycle.

    Fields:
        position_id: Unique identifier for this position record.
        event_key: Market event key this position belongs to.
        side: Trade direction — "YES" or "NO".
        status: Current lifecycle state (OPEN or CLOSED).
        trigger_price: Price at which the entry rule was triggered.
        order_submitted_price: Price at which the order was submitted.
        fill_price: Actual fill price (entry_fill_price from execution).
        trigger_move_value: Price move from trigger to fill at entry.
        fill_move_value: Price move from fill to current at exit (0.0 if open).
        requested_size: Size requested when entering the position.
        filled_size: Actual filled size.
        entry_reason: Rule or condition that triggered entry.
        exit_reason: Rule or condition that triggered exit. Empty if still open.
        opened_at: ISO 8601 UTC timestamp when position was opened.
        closed_at: ISO 8601 UTC timestamp when position was closed. None if open.
    """

    position_id: str
    event_key: str
    side: str
    status: PositionState
    trigger_price: float
    order_submitted_price: float
    fill_price: float
    trigger_move_value: float
    fill_move_value: float
    requested_size: float
    filled_size: float
    entry_reason: str
    exit_reason: str
    opened_at: str
    closed_at: Optional[str] = field(default=None)
