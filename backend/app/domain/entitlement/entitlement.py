"""Entitlement domain model — v1.0.5."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from app.domain.entitlement.license_status import LicenseStatus


@dataclass
class Entitlement:
    """Per-user entitlement and license state.

    trading_enabled is the authoritative gate for all trading actions.
    It is False when license_status != active OR expires_at < now.
    """
    user_id: str
    license_status: LicenseStatus = LicenseStatus.inactive
    expires_at: Optional[datetime] = None
    trading_enabled: bool = False
    allowed_features: List[str] = field(default_factory=list)
    visible_panels: List[str] = field(default_factory=list)
    visible_rules: List[str] = field(default_factory=list)
    editable_rules: List[str] = field(default_factory=list)
    blocked_reason_messages: List[str] = field(default_factory=list)
