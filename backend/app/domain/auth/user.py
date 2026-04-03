"""User domain model — v1.0.6 (session TTL, reset token expiry)."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from app.domain.auth.user_role import UserRole


@dataclass
class User:
    """Authenticated user record."""
    user_id: str
    email: str
    password_hash: str
    role: UserRole = UserRole.user
    session_token: Optional[str] = None
    session_created_at: Optional[datetime] = None
    session_expires_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_requested_at: Optional[datetime] = None
    password_reset_expires_at: Optional[datetime] = None
    is_active: bool = True
