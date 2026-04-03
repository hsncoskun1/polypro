"""Auth API routes — login, logout, forgot/reset password — v1.0.5."""
from fastapi import APIRouter, HTTPException, Request

from app.api.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    ResetPasswordRequest,
)
from app.domain.auth import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _get_auth_store(request: Request):
    return request.app.state.auth_store


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, request: Request):
    store = _get_auth_store(request)
    user = store.get_user_by_email(body.email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_service.login(user, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    store.save_user(user)
    return LoginResponse(
        session_token=token,
        user_id=user.user_id,
        email=user.email,
        role=user.role.value,
    )


@router.post("/logout", status_code=204)
def logout(body: LogoutRequest, request: Request):
    store = _get_auth_store(request)
    user = store.get_user_by_session_token(body.session_token)
    if user is None:
        return  # Idempotent logout
    auth_service.logout(user)
    store.save_user(user)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(body: ForgotPasswordRequest, request: Request):
    store = _get_auth_store(request)
    user = store.get_user_by_email(body.email)
    if user is None:
        # Don't reveal if email exists — return a dummy token-shaped response
        return ForgotPasswordResponse(reset_token="")
    token = auth_service.request_password_reset(user)
    store.save_user(user)
    # In production: send email. For foundation: return token directly.
    return ForgotPasswordResponse(reset_token=token)


@router.post("/reset-password", status_code=204)
def reset_password(body: ResetPasswordRequest, request: Request):
    store = _get_auth_store(request)
    user = store.get_user_by_email(body.email)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid reset request")
    success = auth_service.reset_password(user, body.reset_token, body.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    store.save_user(user)
