"""
Users.xlsx access layer.
"""
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from app.core.config import get_settings
from app.core.security import hash_password
from app.excel_engine.base import ensure_file, read_sheet, atomic_write_sheet, append_row, next_id
from app.excel_engine import logs as log_engine

settings = get_settings()
SHEET = "Users"

VALID_ROLES = {"SUPER_ADMIN", "ADMIN", "SUPPORT", "USER"}
VALID_STATUSES = {"ACTIVE", "SUSPENDED", "PENDING", "DELETED"}


def init():
    ensure_file(settings.USERS_FILE, SHEET)


class DuplicateUserError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_user(full_name: str, phone_number: str, whatsapp_number: str,
                 password: str, role: str = "USER") -> dict:
    init()
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role: {role}")

    df = read_sheet(settings.USERS_FILE, SHEET)

    if not df.empty and (df["Phone Number"].astype(str) == str(phone_number)).any():
        raise DuplicateUserError(f"User with phone number {phone_number} already exists")

    user_id = next_id(df, "User ID", "USR")
    row = {
        "User ID": user_id,
        "Full Name": full_name,
        "Phone Number": phone_number,
        "WhatsApp Number": whatsapp_number,
        "Password Hash": hash_password(password),
        "Role": role,
        "Registration Date": _now(),
        "Status": "ACTIVE",
        "Last Activity": _now(),
    }
    append_row(settings.USERS_FILE, SHEET, row)
    log_engine.log_event("USER_CREATED", description=f"User {user_id} ({phone_number}) created", actor="system")
    safe = dict(row)
    safe.pop("Password Hash", None)
    return safe


def get_user_by_id(user_id: str) -> Optional[dict]:
    init()
    df = read_sheet(settings.USERS_FILE, SHEET)
    match = df[df["User ID"] == user_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_user_by_phone(phone_number: str) -> Optional[dict]:
    init()
    df = read_sheet(settings.USERS_FILE, SHEET)
    if df.empty:
        return None
    match = df[df["Phone Number"].astype(str) == str(phone_number)]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_user_by_whatsapp(whatsapp_number: str) -> Optional[dict]:
    init()
    df = read_sheet(settings.USERS_FILE, SHEET)
    if df.empty:
        return None
    match = df[df["WhatsApp Number"].astype(str) == str(whatsapp_number)]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def list_users(status: Optional[str] = None, search: Optional[str] = None,
                page: int = 1, page_size: int = 20) -> dict:
    init()
    df = read_sheet(settings.USERS_FILE, SHEET)
    if status:
        df = df[df["Status"] == status]
    if search:
        s = search.lower()
        mask = (
            df["Full Name"].astype(str).str.lower().str.contains(s, na=False)
            | df["Phone Number"].astype(str).str.contains(s, na=False)
        )
        df = df[mask]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end].drop(columns=["Password Hash"], errors="ignore")
    page_df = page_df.astype(object).where(page_df.notna(), None)
    return {"total": total, "page": page, "page_size": page_size, "users": page_df.to_dict(orient="records")}


def update_user(user_id: str, updates: dict, actor: str = "system") -> dict:
    init()
    df = read_sheet(settings.USERS_FILE, SHEET)
    idx = df.index[df["User ID"] == user_id]
    if idx.empty:
        raise UserNotFoundError(user_id)

    allowed_fields = {"Full Name", "Phone Number", "WhatsApp Number", "Status", "Role"}
    for key, value in updates.items():
        if key in allowed_fields:
            if key == "Status" and value not in VALID_STATUSES:
                raise ValueError(f"Invalid status: {value}")
            if key == "Role" and value not in VALID_ROLES:
                raise ValueError(f"Invalid role: {value}")
            df.loc[idx, key] = value
    df.loc[idx, "Last Activity"] = _now()
    atomic_write_sheet(settings.USERS_FILE, SHEET, df)
    log_engine.log_event("USER_UPDATED", description=f"User {user_id} updated: {list(updates.keys())}", actor=actor)
    return get_user_by_id(user_id)


def suspend_user(user_id: str, actor: str = "system") -> dict:
    return update_user(user_id, {"Status": "SUSPENDED"}, actor=actor)


def activate_user(user_id: str, actor: str = "system") -> dict:
    return update_user(user_id, {"Status": "ACTIVE"}, actor=actor)


def delete_user(user_id: str, actor: str = "system") -> dict:
    """Soft delete: mark as DELETED rather than removing the row (audit trail)."""
    result = update_user(user_id, {"Status": "DELETED"}, actor=actor)
    log_engine.log_event("USER_DELETED", description=f"User {user_id} deleted", actor=actor)
    return result


def touch_last_activity(user_id: str):
    init()
    df = read_sheet(settings.USERS_FILE, SHEET)
    idx = df.index[df["User ID"] == user_id]
    if idx.empty:
        return
    df.loc[idx, "Last Activity"] = _now()
    atomic_write_sheet(settings.USERS_FILE, SHEET, df)


def count_users() -> dict:
    init()
    df = read_sheet(settings.USERS_FILE, SHEET)
    if df.empty:
        return {"total": 0, "active": 0, "suspended": 0, "new_today": 0}
    today = datetime.now(timezone.utc).date().isoformat()
    new_today = df["Registration Date"].astype(str).str.startswith(today).sum()
    return {
        "total": len(df),
        "active": int((df["Status"] == "ACTIVE").sum()),
        "suspended": int((df["Status"] == "SUSPENDED").sum()),
        "new_today": int(new_today),
    }
