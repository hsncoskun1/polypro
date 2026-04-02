"""Live order reconciliation result model — v0.7.6."""
from dataclasses import dataclass
from typing import Optional
from app.domain.live.reconciliation_status import ReconciliationStatus
from app.domain.live.live_order_state import LiveOrderState


@dataclass
class LiveOrderReconciliationResult:
    order_id: str
    reconciliation_status: ReconciliationStatus
    final_state: Optional[LiveOrderState] = None
    events_processed: int = 0
    is_terminal: bool = False
    reconciled_at: str = ""
