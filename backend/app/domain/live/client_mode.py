"""Client mode enum — v0.7.9."""
from enum import Enum


class ClientMode(str, Enum):
    SIMULATION_MOCK = "simulation_mock"
    LIVE_MOCK = "live_mock"
    LIVE_DRY_RUN = "live_dry_run"
    LIVE_PRODUCTION = "live_production"
