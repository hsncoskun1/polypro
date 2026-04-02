"""Launcher readiness state model.

Represents the current completion state of mandatory launcher steps.
All fields default to the most restrictive (blocked) state.
Runtime state is never directly edited — evaluator reads this as input.
"""
from dataclasses import dataclass


@dataclass
class ReadinessState:
    """Current state of all mandatory launcher readiness conditions."""
    setup_completed: bool = False
    update_required: bool = False
    preflight_passed: bool = False
