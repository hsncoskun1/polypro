"""Auth API schemas — v1.0.5."""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    session_token: str
    user_id: str
    email: str
    role: str


class LogoutRequest(BaseModel):
    session_token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    reset_token: str  # In production this would be emailed, not returned


class ResetPasswordRequest(BaseModel):
    email: str
    reset_token: str
    new_password: str


class EntitlementResponse(BaseModel):
    user_id: str
    license_status: str
    expires_at: Optional[str]
    trading_enabled: bool
    allowed_features: List[str]
    visible_panels: List[str]
    visible_rules: List[str]
    editable_rules: List[str]
    blocked_reason_messages: List[str]


class AdminUserSummary(BaseModel):
    user_id: str
    email: str
    role: str
    is_active: bool
    last_login_at: Optional[str]
    license_status: Optional[str]
    trading_enabled: bool


class AdminSummaryResponse(BaseModel):
    online_user_count: int
    total_user_count: int
    active_bot_count: int
    open_position_count: int
    closed_position_count: int
    blocked_trade_count: int
    alert_count: int


class AdminEntitlementUpdateRequest(BaseModel):
    license_status: str
    expires_at: Optional[str] = None
    trading_enabled: bool = False
    allowed_features: List[str] = []
    visible_panels: List[str] = []
    visible_rules: List[str] = []
    editable_rules: List[str] = []
    blocked_reason_messages: List[str] = []
