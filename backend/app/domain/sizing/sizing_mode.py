"""SizingMode — order sizing method enum."""
from enum import Enum


class SizingMode(str, Enum):
    FIXED_AMOUNT = "fixed_amount"
    AVAILABLE_BALANCE_PERCENT = "available_balance_percent"
