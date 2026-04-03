"""SQLite-backed auth store for users and entitlements — v1.0.5."""
from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from app.domain.auth.user import User
from app.domain.auth.user_role import UserRole
from app.domain.entitlement.entitlement import Entitlement
from app.domain.entitlement.license_status import LicenseStatus


class AuthStore:
    """SQLite store for users and entitlements."""

    def __init__(self, db_path: str = "data/auth.db") -> None:
        self._db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    session_token TEXT,
                    last_login_at TEXT,
                    password_reset_token TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entitlements (
                    user_id TEXT PRIMARY KEY,
                    license_status TEXT NOT NULL DEFAULT 'inactive',
                    expires_at TEXT,
                    trading_enabled INTEGER NOT NULL DEFAULT 0,
                    allowed_features TEXT NOT NULL DEFAULT '[]',
                    visible_panels TEXT NOT NULL DEFAULT '[]',
                    visible_rules TEXT NOT NULL DEFAULT '[]',
                    editable_rules TEXT NOT NULL DEFAULT '[]',
                    blocked_reason_messages TEXT NOT NULL DEFAULT '[]'
                )
            """)

    # --- User CRUD ---

    def save_user(self, user: User) -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO users
                (user_id, email, password_hash, role, session_token, last_login_at,
                 password_reset_token, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.user_id,
                user.email,
                user.password_hash,
                user.role.value,
                user.session_token,
                user.last_login_at.isoformat() if user.last_login_at else None,
                user.password_reset_token,
                1 if user.is_active else 0,
            ))

    def get_user_by_email(self, email: str) -> Optional[User]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def get_user_by_session_token(self, token: str) -> Optional[User]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE session_token = ?", (token,)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def list_users(self) -> List[User]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
        return [self._row_to_user(r) for r in rows]

    def _row_to_user(self, row: sqlite3.Row) -> User:
        last_login = None
        if row["last_login_at"]:
            last_login = datetime.fromisoformat(row["last_login_at"])
        return User(
            user_id=row["user_id"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=UserRole(row["role"]),
            session_token=row["session_token"],
            last_login_at=last_login,
            password_reset_token=row["password_reset_token"],
            is_active=bool(row["is_active"]),
        )

    # --- Entitlement CRUD ---

    def save_entitlement(self, ent: Entitlement) -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO entitlements
                (user_id, license_status, expires_at, trading_enabled,
                 allowed_features, visible_panels, visible_rules, editable_rules,
                 blocked_reason_messages)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ent.user_id,
                ent.license_status.value,
                ent.expires_at.isoformat() if ent.expires_at else None,
                1 if ent.trading_enabled else 0,
                json.dumps(ent.allowed_features),
                json.dumps(ent.visible_panels),
                json.dumps(ent.visible_rules),
                json.dumps(ent.editable_rules),
                json.dumps(ent.blocked_reason_messages),
            ))

    def get_entitlement(self, user_id: str) -> Optional[Entitlement]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM entitlements WHERE user_id = ?", (user_id,)
            ).fetchone()
        return self._row_to_entitlement(row) if row else None

    def _row_to_entitlement(self, row: sqlite3.Row) -> Entitlement:
        expires = None
        if row["expires_at"]:
            expires = datetime.fromisoformat(row["expires_at"])
        return Entitlement(
            user_id=row["user_id"],
            license_status=LicenseStatus(row["license_status"]),
            expires_at=expires,
            trading_enabled=bool(row["trading_enabled"]),
            allowed_features=json.loads(row["allowed_features"]),
            visible_panels=json.loads(row["visible_panels"]),
            visible_rules=json.loads(row["visible_rules"]),
            editable_rules=json.loads(row["editable_rules"]),
            blocked_reason_messages=json.loads(row["blocked_reason_messages"]),
        )

    def count_active_sessions(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM users WHERE session_token IS NOT NULL AND is_active = 1"
            ).fetchone()
        return row["cnt"] if row else 0
