"""Verification gate context model.

Represents the inputs to the verification gate check.
All fields default to the most restrictive (invalid/not-ok) state.
This is separate from strategy entry decision — verification is an additional
hard-block layer that must pass before any trade is allowed.
"""
from dataclasses import dataclass


@dataclass
class VerificationContext:
    """Current validity state of all mandatory pre-trade checks."""
    ref_valid: bool = False
    market_valid: bool = False
    settings_ok: bool = False
