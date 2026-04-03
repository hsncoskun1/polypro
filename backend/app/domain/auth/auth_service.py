"""Auth service — v1.0.6 (bcrypt hashing, session TTL, reset token expiry)."""
from __future__ import annotations
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt

from app.domain.auth.user import User
from app.domain.auth.user_role import UserRole

# Session TTL: 24 hours by default
SESSION_TTL_HOURS: int = 24

# Reset token TTL: 1 hour
RESET_TOKEN_TTL_MINUTES: int = 60


def hash_password(plain: str) -> str:
    """Hash password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify bcrypt password hash."""
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def generate_session_token() -> str:
    return secrets.token_hex(32)


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def create_user(email: str, password: str, role: UserRole = UserRole.user) -> User:
    return User(
        user_id=str(uuid.uuid4()),
        email=email,
        password_hash=hash_password(password),
        role=role,
    )


def login(user: User, password: str, ttl_hours: int = SESSION_TTL_HOURS) -> Optional[str]:
    """Verify password and return session token on success, None on failure.

    Creates session with expiry = now + ttl_hours.
    """
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    now = datetime.now(timezone.utc)
    token = generate_session_token()
    user.session_token = token
    user.session_created_at = now
    user.session_expires_at = now + timedelta(hours=ttl_hours)
    user.last_login_at = now
    return token


def logout(user: User) -> None:
    user.session_token = None
    user.session_created_at = None
    user.session_expires_at = None


def is_session_valid(user: User) -> bool:
    """Return True if session token exists and has not expired."""
    if user.session_token is None:
        return False
    if user.session_expires_at is None:
        return False
    now = datetime.now(timezone.utc)
    expires = user.session_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return now < expires


def request_password_reset(
    user: User,
    ttl_minutes: int = RESET_TOKEN_TTL_MINUTES,
) -> str:
    """Generate a time-limited, single-use reset token."""
    now = datetime.now(timezone.utc)
    token = generate_reset_token()
    user.password_reset_token = token
    user.password_reset_requested_at = now
    user.password_reset_expires_at = now + timedelta(minutes=ttl_minutes)
    return token


def reset_password(user: User, reset_token: str, new_password: str) -> bool:
    """Verify reset token (must match, not expired, single-use). Returns True on success."""
    if user.password_reset_token is None:
        return False
    if user.password_reset_token != reset_token:
        return False
    if user.password_reset_expires_at is None:
        return False
    now = datetime.now(timezone.utc)
    expires = user.password_reset_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if now > expires:
        return False
    # Success: update password and invalidate token (single-use)
    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_requested_at = None
    user.password_reset_expires_at = None
    user.session_token = None
    user.session_created_at = None
    user.session_expires_at = None
    return True
