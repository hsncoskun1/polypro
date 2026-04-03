"""SQLite-backed auth store — v1.1.2 (policy audit trail)."""
from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from app.domain.auth.user import User
from app.domain.auth.user_role import UserRole
from app.domain.audit.policy_audit_record import PolicyAuditRecord
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
                    session_created_at TEXT,
                    session_expires_at TEXT,
                    last_login_at TEXT,
                    password_reset_token TEXT,
                    password_reset_requested_at TEXT,
                    password_reset_expires_at TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1
                )
            """)
            # Migration: add new columns if they don't exist (for existing DBs)
            existing = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
            for col, definition in [
                ("session_created_at", "TEXT"),
                ("session_expires_at", "TEXT"),
                ("password_reset_requested_at", "TEXT"),
                ("password_reset_expires_at", "TEXT"),
            ]:
                if col not in existing:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")

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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS policy_audit_log (
                    audit_id TEXT PRIMARY KEY,
                    actor_id TEXT NOT NULL,
                    target_user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    snapshot_before TEXT NOT NULL DEFAULT '{}',
                    snapshot_after TEXT NOT NULL DEFAULT '{}',
                    changed_at TEXT NOT NULL
                )
            """)

    # --- User CRUD ---

    def save_user(self, user: User) -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO users
                (user_id, email, password_hash, role, session_token,
                 session_created_at, session_expires_at, last_login_at,
                 password_reset_token, password_reset_requested_at,
                 password_reset_expires_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.user_id,
                user.email,
                user.password_hash,
                user.role.value,
                user.session_token,
                user.session_created_at.isoformat() if user.session_created_at else None,
                user.session_expires_at.isoformat() if user.session_expires_at else None,
                user.last_login_at.isoformat() if user.last_login_at else None,
                user.password_reset_token,
                user.password_reset_requested_at.isoformat() if user.password_reset_requested_at else None,
                user.password_reset_expires_at.isoformat() if user.password_reset_expires_at else None,
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

    def _parse_dt(self, val) -> Optional[datetime]:
        if not val:
            return None
        dt = datetime.fromisoformat(val)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def _row_to_user(self, row: sqlite3.Row) -> User:
        keys = row.keys()
        return User(
            user_id=row["user_id"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=UserRole(row["role"]),
            session_token=row["session_token"],
            session_created_at=self._parse_dt(row["session_created_at"] if "session_created_at" in keys else None),
            session_expires_at=self._parse_dt(row["session_expires_at"] if "session_expires_at" in keys else None),
            last_login_at=self._parse_dt(row["last_login_at"]),
            password_reset_token=row["password_reset_token"],
            password_reset_requested_at=self._parse_dt(row["password_reset_requested_at"] if "password_reset_requested_at" in keys else None),
            password_reset_expires_at=self._parse_dt(row["password_reset_expires_at"] if "password_reset_expires_at" in keys else None),
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
        return Entitlement(
            user_id=row["user_id"],
            license_status=LicenseStatus(row["license_status"]),
            expires_at=self._parse_dt(row["expires_at"]),
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

    # --- Policy Audit Log ---

    def save_policy_audit_record(self, record: PolicyAuditRecord) -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO policy_audit_log
                (audit_id, actor_id, target_user_id, action, snapshot_before, snapshot_after, changed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record.audit_id,
                record.actor_id,
                record.target_user_id,
                record.action,
                json.dumps(record.snapshot_before),
                json.dumps(record.snapshot_after),
                record.changed_at.isoformat(),
            ))

    def get_policy_audit_records(self, target_user_id: str) -> List[PolicyAuditRecord]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM policy_audit_log WHERE target_user_id = ? ORDER BY changed_at DESC",
                (target_user_id,)
            ).fetchall()
        return [self._row_to_audit_record(r) for r in rows]

    def _row_to_audit_record(self, row: sqlite3.Row) -> PolicyAuditRecord:
        return PolicyAuditRecord(
            audit_id=row["audit_id"],
            actor_id=row["actor_id"],
            target_user_id=row["target_user_id"],
            action=row["action"],
            snapshot_before=json.loads(row["snapshot_before"]),
            snapshot_after=json.loads(row["snapshot_after"]),
            changed_at=self._parse_dt(row["changed_at"]) or datetime.now(timezone.utc),
        )
