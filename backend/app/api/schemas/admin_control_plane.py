"""AdminControlPlaneResponse — Pydantic response schema for GET /admin/control-plane.

Admin surface shows broader data than the user-facing control plane:
- Full operational control state
- Detailed financial reporting
- Blocked trade/rule/risk event lists
- Execution fill events, claim events, operational alerts
- Release gate visibility

Secrets are never included.
"""
from typing import List
from pydantic import BaseModel


class AdminControlPlaneResponse(BaseModel):
    # Operational control state
    safe_stop_active: bool
    safe_stop_reason: str
    scheduler_enabled: bool
    global_disable_active: bool
    config_reload_available: bool
    config_reset_available: bool

    # Financial reporting
    total_balance: float
    available_balance: float
    current_balance: float
    session_start_balance: float
    realized_pnl: float
    unrealized_pnl: float
    session_total_pnl: float
    claim_adjusted_balance_effect: float

    # Operational event lists
    blocked_trades: List[str]
    blocked_rules: List[str]
    blocked_risk_events: List[str]
    execution_fill_events: List[str]
    claim_events: List[str]
    operational_alerts: List[str]

    # Release gate
    release_ready: bool
    live_applied_testing_ready: bool
