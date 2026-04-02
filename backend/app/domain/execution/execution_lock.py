"""Execution lock — in-memory duplicate entry guard.

Tracks which event_keys currently have an open simulation position.
Designed as a seam: can be replaced with a persistent lock store in v0.5.2+
without changing the executor interface.
"""
from dataclasses import dataclass, field


@dataclass
class ExecutionLock:
    """In-memory set of locked event keys.

    An event_key is locked from the moment simulate_entry succeeds until
    simulate_exit releases it. A second entry attempt for a locked key
    is rejected as a duplicate.
    """

    _locked: set = field(default_factory=set)

    def is_locked(self, event_key: str) -> bool:
        """Return True if the event_key has an open position."""
        return event_key in self._locked

    def acquire(self, event_key: str) -> None:
        """Lock the event_key — called on successful entry."""
        self._locked.add(event_key)

    def release(self, event_key: str) -> None:
        """Unlock the event_key — called on exit."""
        self._locked.discard(event_key)
