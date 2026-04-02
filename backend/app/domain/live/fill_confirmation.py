"""Fill confirmation read model — v0.7.4.

Separate read model for fill confirmation lifecycle.
Seam for future accounting/persistence integration (v0.5.3/v0.5.4 compatibility).
"""
from dataclasses import dataclass
from app.domain.live.fill_confirmation_status import FillConfirmationStatus


@dataclass
class FillConfirmation:
    order_id: str
    fill_confirmation_status: FillConfirmationStatus

    # Size accounting
    requested_size: float
    filled_size: float = 0.0
    remaining_size: float = 0.0

    # Audit
    fill_confirmed_at: str = ""
