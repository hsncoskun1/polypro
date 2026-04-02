"""Fill confirmation status enum — v0.7.4."""
from enum import Enum


class FillConfirmationStatus(str, Enum):
    NOT_CONFIRMED = "not_confirmed"
    PARTIALLY_CONFIRMED = "partially_confirmed"
    FULLY_CONFIRMED = "fully_confirmed"
    CONFIRMATION_FAILED = "confirmation_failed"
