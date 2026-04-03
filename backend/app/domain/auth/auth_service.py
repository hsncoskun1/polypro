"""Auth service — login, logout, password reset — v1.0.5."""
from __future__ import annotations
import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.domain.auth.user import User
from app.domain.auth.user_role import UserRole


def _hash_password(password: str) -> str:
    """SHA-256 password hash. Production should use bcrypt."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return _hash_password(plain) == hashed


def hash_password(plain: str) -> str:
    return _hash_password(plain)


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


def login(user: User, password: str) -> Optional[str]:
    """Verify password and return session token on success, None on failure."""
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    token = generate_session_token()
    user.session_token = token
    user.last_login_at = datetime.now(timezone.utc)
    return token


def logout(user: User) -> None:
    user.session_token = None


def request_password_reset(user: User) -> str:
    token = generate_reset_token()
    user.password_reset_token = token
    return token


def reset_password(user: User, reset_token: str, new_password: str) -> bool:
    if user.password_reset_token != reset_token:
        return False
    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.session_token = None
    return True
