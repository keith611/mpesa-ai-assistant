"""
Authentication endpoints: register, login, logout, refresh, password reset.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from jose import JWTError
from pydantic import BaseModel

from app.models.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.deps import get_current_claims
from app.db_engine import users as user_engine
from app.db_engine import logs as log_engine
from app.services import password_reset

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Simple denylist for logged-out refresh tokens (swap for Redis in production).
_revoked_tokens: set[str] = set()


class ForgotPasswordRequest(BaseModel):
    phone_number: str


class ResetPasswordRequest(BaseModel):
    phone_number: str
    code: str
    new_password: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    try:
        user = user_engine.create_user(
            full_name=payload.full_name,
            phone_number=payload.phone_number,
            whatsapp_number=payload.whatsapp_number,
            password=payload.password,
            role="USER",
        )
    except user_engine.DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    access_token = create_access_token(subject=user["User ID"], role=user["Role"])
    refresh_token = create_refresh_token(subject=user["User ID"])
    log_engine.log_event("USER_REGISTERED", description=user["User ID"], actor=user["User ID"])
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = user_engine.get_user_by_phone(payload.phone_number)
    if not user or not verify_password(payload.password, user.get("Password Hash", "")):
        log_engine.log_event("LOGIN_FAILED", status="ERROR", description=payload.phone_number)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone number or password")

    if user.get("Status") != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Account is {user.get('Status')}")

    user_engine.touch_last_activity(user["User ID"])
    access_token = create_access_token(subject=user["User ID"], role=user["Role"])
    refresh_token = create_refresh_token(subject=user["User ID"])
    log_engine.log_event("LOGIN_SUCCESS", actor=user["User ID"])
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    if payload.refresh_token in _revoked_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    try:
        claims = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    if claims.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token")

    user = user_engine.get_user_by_id(claims["sub"])
    if not user or user.get("Status") != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")

    new_access = create_access_token(subject=user["User ID"], role=user["Role"])
    new_refresh = create_refresh_token(subject=user["User ID"])
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, claims: dict = Depends(get_current_claims)):
    _revoked_tokens.add(payload.refresh_token)
    log_engine.log_event("LOGOUT", actor=claims.get("sub"))
    return None


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    """
    Requests a one-time reset code, delivered back to the user over
    WhatsApp. Always returns a generic response, whether or not the
    phone number is registered, so this can't be used to enumerate
    accounts. If the account exists, the code is also sent as a WhatsApp
    message immediately.
    """
    result = password_reset.request_reset_code(payload.phone_number)
    if result.get("code"):
        from app.services.whatsapp.factory import get_whatsapp_service
        user = user_engine.get_user_by_phone(payload.phone_number)
        if user:
            service = get_whatsapp_service()
            service.send_text_message(
                user["WhatsApp Number"],
                f"🔐 Your M-Pesa AI Assistant password reset code is {result['code']}. "
                f"It expires in {result['expires_in_minutes']} minutes. "
                f"If you didn't request this, you can ignore this message.",
            )
    return {"message": "If that phone number is registered, a reset code has been sent via WhatsApp."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    try:
        password_reset.confirm_reset(payload.phone_number, payload.code, payload.new_password)
    except password_reset.ResetError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Password reset successfully. You can now sign in with your new password."}
