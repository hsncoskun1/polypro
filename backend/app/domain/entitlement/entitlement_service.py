"""Entitlement service — license enforcement — v1.0.5."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

from app.domain.entitlement.entitlement import Entitlement
from app.domain.entitlement.license_status import LicenseStatus


def compute_trading_enabled(entitlement: Entitlement) -> bool:
    """Return True only if license is active and not expired."""
    if entitlement.license_status != LicenseStatus.active:
        return False
    if entitlement.expires_at is not None:
        now = datetime.now(timezone.utc)
        expires = entitlement.expires_at
        # Make expires tz-aware if naive
        if expires.tzinfo is None:
            from datetime import timezone as tz
            expires = expires.replace(tzinfo=tz.utc)
        if now > expires:
            return False
    return True


def apply_license_enforcement(entitlement: Entitlement) -> Entitlement:
    """Recompute trading_enabled and append blocked reason if trading blocked."""
    enabled = compute_trading_enabled(entitlement)
    entitlement.trading_enabled = enabled
    if not enabled:
        msg = "Trading disabled: license not active or expired."
        if msg not in entitlement.blocked_reason_messages:
            entitlement.blocked_reason_messages = [msg] + [
                m for m in entitlement.blocked_reason_messages if m != msg
            ]
    else:
        entitlement.blocked_reason_messages = [
            m for m in entitlement.blocked_reason_messages
            if m != "Trading disabled: license not active or expired."
        ]
    return entitlement


def is_trading_enabled(entitlement: Optional[Entitlement]) -> bool:
    """Safe check — returns False if entitlement is None."""
    if entitlement is None:
        return False
    return compute_trading_enabled(entitlement)
