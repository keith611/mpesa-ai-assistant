"""
Password reset service.

Two flows, sharing this core logic:
1. Admin-assisted: an ADMIN/SUPER_ADMIN generates a temporary password for
   a user directly (see /users/{user_id}/reset-password in api/users.py).
2. Self-service: the user requests a one-time code (via the app or by
   messaging the WhatsApp bot "reset password"), the code is delivered
   back over WhatsApp, then they confirm it along with a new password.

Reset codes are short-lived and held in memory (not persisted to the
database — they're ephemeral by design). For a multi-instance deployment,
swap this for a shared store (Redis etc.) the same way the JWT denylist
would need to be swapped.
"""
import random
import secrets
import string
import threading
from datetime import datetime, timedelta, timezone

from app.db_engine import users as user_engine
from app.db_engine import logs as log_engine
from app.core.security import hash_password

CODE_TTL_MINUTES = 10

_lock = threading.Lock()
_pending_codes: dict[str, tuple[str, datetime]] = {}  # phone_number -> (code, expires_at)


class ResetError(Exception):
    pass


def _generate_code() -> str:
    return "".join(random.choices(string.digits, k=6))


def request_reset_code(phone_number: str) -> dict:
    """
    Generates a one-time code for the account with this phone number.
    Always returns a generic success shape regardless of whether the
    phone number exists, so this endpoint can't be used to enumerate
    registered accounts. The code itself is only returned here when the
    user genuinely exists (callers should relay it back to the user via
    WhatsApp / the app — never log it or expose it otherwise).
    """
    user = user_engine.get_user_by_phone(phone_number)
    if not user or user.get("Status") != "ACTIVE":
        # Same response shape either way — don't reveal account existence.
        return {"sent": True, "code": None}

    code = _generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES)
    with _lock:
        _pending_codes[phone_number] = (code, expires_at)

    log_engine.log_event("PASSWORD_RESET_REQUESTED", description=f"user={user['User ID']}", actor=user["User ID"])
    return {"sent": True, "code": code, "expires_in_minutes": CODE_TTL_MINUTES}


def confirm_reset(phone_number: str, code: str, new_password: str) -> dict:
    if len(new_password) < 8:
        raise ResetError("Password must be at least 8 characters.")

    with _lock:
        entry = _pending_codes.get(phone_number)

    if not entry:
        raise ResetError("No reset code was requested for this number, or it already expired.")

    stored_code, expires_at = entry
    if datetime.now(timezone.utc) > expires_at:
        with _lock:
            _pending_codes.pop(phone_number, None)
        raise ResetError("This reset code has expired. Request a new one.")

    if code.strip() != stored_code:
        raise ResetError("Incorrect reset code.")

    user = user_engine.get_user_by_phone(phone_number)
    if not user:
        raise ResetError("Account not found.")

    user_engine.update_user(user["User ID"], {}, actor=user["User ID"])  # touches Last Activity
    _set_password_hash(user["User ID"], new_password)

    with _lock:
        _pending_codes.pop(phone_number, None)

    log_engine.log_event("PASSWORD_RESET_COMPLETED", description=f"user={user['User ID']}", actor=user["User ID"])
    return {"status": "password_reset"}


def admin_reset_password(user_id: str, actor: str) -> str:
    """Generates a fresh temporary password, sets it directly, and returns it to the admin to relay."""
    user = user_engine.get_user_by_id(user_id)
    if not user:
        raise ResetError("User not found.")

    temp_password = secrets.token_urlsafe(9)  # readable-ish, ~12 chars
    _set_password_hash(user_id, temp_password)
    log_engine.log_event("PASSWORD_RESET_BY_ADMIN", description=f"user={user_id}", actor=actor)
    return temp_password


def _set_password_hash(user_id: str, new_password: str):
    try:
        user_engine.set_password_hash(user_id, hash_password(new_password))
    except user_engine.UserNotFoundError:
        raise ResetError("User not found.")
