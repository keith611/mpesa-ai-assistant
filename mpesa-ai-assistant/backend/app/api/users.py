"""
User management endpoints. Admin-level roles only, except for a user
fetching/updating their own profile.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query

from app.models.schemas import UserUpdateRequest
from app.core.deps import get_current_claims, require_min_role
from app.db_engine import users as user_engine
from app.services import password_reset

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_my_profile(claims: dict = Depends(get_current_claims)):
    user = user_engine.get_user_by_id(claims["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.pop("Password Hash", None)
    return user


@router.get("", dependencies=[Depends(require_min_role("SUPPORT"))])
def list_users(status_filter: Optional[str] = Query(None, alias="status"),
               search: Optional[str] = None, page: int = 1, page_size: int = 20):
    return user_engine.list_users(status=status_filter, search=search, page=page, page_size=page_size)


@router.get("/{user_id}", dependencies=[Depends(require_min_role("SUPPORT"))])
def get_user(user_id: str):
    user = user_engine.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.pop("Password Hash", None)
    return user


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_min_role("ADMIN"))])
def create_user_admin(full_name: str, phone_number: str, whatsapp_number: str,
                       password: str, role: str = "USER"):
    try:
        return user_engine.create_user(full_name, phone_number, whatsapp_number, password, role)
    except user_engine.DuplicateUserError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}", dependencies=[Depends(require_min_role("ADMIN"))])
def update_user(user_id: str, payload: UserUpdateRequest, claims: dict = Depends(get_current_claims)):
    updates = {}
    if payload.full_name is not None:
        updates["Full Name"] = payload.full_name
    if payload.phone_number is not None:
        updates["Phone Number"] = payload.phone_number
    if payload.whatsapp_number is not None:
        updates["WhatsApp Number"] = payload.whatsapp_number
    if payload.status is not None:
        updates["Status"] = payload.status
    if payload.role is not None:
        updates["Role"] = payload.role
    try:
        return user_engine.update_user(user_id, updates, actor=claims["sub"])
    except user_engine.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{user_id}/suspend", dependencies=[Depends(require_min_role("ADMIN"))])
def suspend_user(user_id: str, claims: dict = Depends(get_current_claims)):
    try:
        return user_engine.suspend_user(user_id, actor=claims["sub"])
    except user_engine.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/{user_id}/activate", dependencies=[Depends(require_min_role("ADMIN"))])
def activate_user(user_id: str, claims: dict = Depends(get_current_claims)):
    try:
        return user_engine.activate_user(user_id, actor=claims["sub"])
    except user_engine.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/{user_id}/reset-password", dependencies=[Depends(require_min_role("ADMIN"))])
def reset_user_password(user_id: str, claims: dict = Depends(get_current_claims)):
    """
    Generates a fresh temporary password for a user and returns it to the
    admin, who is responsible for relaying it to the user through a
    trusted channel. The user should change it after logging in.
    """
    try:
        temp_password = password_reset.admin_reset_password(user_id, actor=claims["sub"])
        return {"user_id": user_id, "temporary_password": temp_password}
    except password_reset.ResetError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}", dependencies=[Depends(require_min_role("SUPER_ADMIN"))])
def delete_user(user_id: str, claims: dict = Depends(get_current_claims)):
    try:
        return user_engine.delete_user(user_id, actor=claims["sub"])
    except user_engine.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
