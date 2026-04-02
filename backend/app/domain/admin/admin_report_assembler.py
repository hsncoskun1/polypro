"""admin_report_assembler — assembles AdminReportSnapshot from domain data.

Pure assembler — does not compute values.
All values come from upstream domain evaluators (accounting, risk, claim, control).
"""
from typing import List
from app.domain.admin.admin_control import AdminControl
from app.domain.admin.admin_report_snapshot import AdminReportSnapshot


def assemble_admin_report_snapshot(
    control: AdminControl,
    total_balance: float,
    available_balance: float,
    session_start_balance: float,
    current_balance: float,
    realized_pnl: float,
    unrealized_pnl: float,
    session_total_pnl: float,
    claim_adjusted_balance_effect: float,
    blocked_trades: List[str],
    blocked_rules: List[str],
    blocked_risk_events: List[str],
    execution_fill_events: List[str],
    claim_events: List[str],
    operational_alerts: List[str],
) -> AdminReportSnapshot:
    """Assemble a full admin report snapshot.

    Operational control state is taken from AdminControl.
    Financial and event data is passed in from upstream evaluators.
    Runtime state is not modified — this is a read-only assembly.
    """
    return AdminReportSnapshot(
        safe_stop_active=control.safe_stop_active,
        safe_stop_reason=control.safe_stop_reason,
        scheduler_enabled=control.scheduler_enabled,
        global_disable_active=control.global_disable_active,
        config_reload_available=control.config_reload_available,
        config_reset_available=control.config_reset_available,
        total_balance=total_balance,
        available_balance=available_balance,
        session_start_balance=session_start_balance,
        current_balance=current_balance,
        realized_pnl=realized_pnl,
        unrealized_pnl=unrealized_pnl,
        session_total_pnl=session_total_pnl,
        claim_adjusted_balance_effect=claim_adjusted_balance_effect,
        blocked_trades=list(blocked_trades),
        blocked_rules=list(blocked_rules),
        blocked_risk_events=list(blocked_risk_events),
        execution_fill_events=list(execution_fill_events),
        claim_events=list(claim_events),
        operational_alerts=list(operational_alerts),
    )
