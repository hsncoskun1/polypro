"""Live mode enum — v0.7.0."""
from enum import Enum


class LiveMode(str, Enum):
    SIMULATION = "simulation"
    LIVE = "live"
