"""AdminControl — operational control surface for admin actions.

Models safe stop, scheduler control, global disable, and config reload/reset.
Does not directly modify runtime state — carries action/decision surface only.
"""
from dataclasses import dataclass


@dataclass
class AdminControl:
    # Safe stop — halts new trade entries, allows existing trades to complete
    safe_stop_active: bool = False
    safe_stop_reason: str = ""

    # Scheduler — controls whether the discovery/trigger scheduler is running
    scheduler_enabled: bool = True

    # Global disable — emergency hard stop of all system activity
    global_disable_active: bool = False

    # Config management seams
    config_reload_available: bool = True
    config_reset_available: bool = True
