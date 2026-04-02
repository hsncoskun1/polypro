"""AdminReportSnapshot — full admin operational + financial read model.

Admin has broader visibility than the user-facing control plane:
- Operational control state (safe stop, scheduler, global disable, config)
- Detailed financial reporting
- Blocked trade/rule/risk events
- Execution and claim event logs
- Operational alerts
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class AdminReportSnapshot:
    # Operational control state
    safe_stop_active: bool = False
    safe_stop_reason: str = ""
    scheduler_enabled: bool = True
    global_disable_active: bool = False
    config_reload_available: bool = True
    config_reset_available: bool = True

    # Financial reporting — full balance/PnL breakdown
    total_balance: float = 0.0
    available_balance: float = 0.0
    session_start_balance: float = 0.0
    current_balance: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    session_total_pnl: float = 0.0
    claim_adjusted_balance_effect: float = 0.0

    # Operational event lists — blocked / fill / claim / alerts
    blocked_trades: List[str] = field(default_factory=list)
    blocked_rules: List[str] = field(default_factory=list)
    blocked_risk_events: List[str] = field(default_factory=list)
    execution_fill_events: List[str] = field(default_factory=list)
    claim_events: List[str] = field(default_factory=list)
    operational_alerts: List[str] = field(default_factory=list)
