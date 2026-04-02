"""Event record model — structured record of a position lifecycle event.

Design decisions:
- Immutable record per event. One EventRecord per lifecycle moment.
- event_key links the record to the market event/position it belongs to.
- timestamp is ISO 8601 UTC string.
- payload is a dict for event-specific data (prices, reasons, etc.).
  Kept flexible for future UI/reporting use without schema lock-in now.
- This foundation is designed to be connectable to a control plane,
  admin reporting, or UI event feed in future scope.
- Persistence of EventRecord is NOT in scope this turn.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.event_log.event_type import EventType


@dataclass
class EventRecord:
    """A single structured lifecycle event record.

    Fields:
        event_type: The type of event (from EventType enum).
        event_key: Market event key this record belongs to.
        timestamp: ISO 8601 UTC timestamp when the event occurred.
        payload: Optional dict with event-specific data (prices, reasons, etc.).
    """

    event_type: EventType
    event_key: str
    timestamp: str
    payload: dict = field(default_factory=dict)
