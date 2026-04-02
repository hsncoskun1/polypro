"""Live order reconciliation status enum — v0.7.6."""
from enum import Enum


class ReconciliationStatus(str, Enum):
    RECONCILED = "reconciled"
    NO_EVENTS = "no_events"
    CONFLICTING_EVENTS = "conflicting_events"
    TERMINAL_STATE = "terminal_state"
