"""Position state enumeration — lifecycle state of a persisted position."""
from enum import Enum


class PositionState(str, Enum):
    """Lifecycle state of a position.

    OPEN: Position has been entered and is active.
    CLOSED: Position has been exited.
    """

    OPEN = "open"
    CLOSED = "closed"
