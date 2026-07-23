"""
Users table access layer (Postgres via SQLAlchemy).

Every function here has the exact same name, signature, and return shape
(dict keys like "User ID", "Full Name", etc.) as the original Excel-based
version, so nothing in api/, services/, or the frontend/Android clients
needs to change — only this module's internals changed.
"""
from datetime import datetime, timezone
from typing import Optional

from app.db.database import get_session, Base, engine
from app.db.models import User
from app.db_engine.helpers import next_id
from app.core.security import hash_password
from app.db_engine import logs as log_engine

VALID_ROLES = {"SUPER_ADMIN", "ADMIN", "SUPPORT", "USER"}
VALID_STATUSES = {"ACTIVE", "SUSPENDED", "PENDING", "DELETED"}


class DuplicateUserError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def init():
    """Creates the table if it doesn't exist yet. Safe to call repeatedly."""
    Base.metadata.create_all(bind=engine, tables=[User.__table__])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_display_dict(u: User, include_hash: bool = False) -> dict:
    d = {
        "User ID": u.user_id,
        "Full Name": u.full_name,
        "Phone Number": u.phone_number,
        "WhatsApp Number": u.whatsapp_number,
        "Role": u.role,
        "Registration Date": u.registration_date,
        "Status": u.status,
        "Last Activity": u.last_activity,
    }
    if include_hash:
        d["Password Hash"] = u.password_hash
    return d


def create_user(full_name: str, phone_number: str, whatsapp_number: str,
                 password: str, role: str = "USER") -> dict:
    init()
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role: {role}")

    with get_session() as session:
        existing = session.query(User).filter(User.phone_number == str(phone_number)).first()
        if existing:
            raise DuplicateUserError(f"User with phone number {phone_number} already exists")

        user_id = next_id(session, User, "user_id", "USR")
        user = User(
            user_id=user_id,
            full_name=full_name,
            phone_number=phone_number,
            whatsapp_number=whatsapp_number,
            password_hash=hash_password(password),
            role=role,
            registration_date=_now(),
            status="ACTIVE",
            last_activity=_now(),
        )
        session.add(user)
        session.flush()
        result = _to_display_dict(user)

    log_engine.log_event("USER_CREATED", description=f"User {user_id} ({phone_number}) created", actor="system")
    return result


def get_user_by_id(user_id: str) -> Optional[dict]:
    init()
    with get_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        return _to_display_dict(user, include_hash=True) if user else None


def get_user_by_phone(phone_number: str) -> Optional[dict]:
    init()
    with get_session() as session:
        user = session.query(User).filter(User.phone_number == str(phone_number)).first()
        return _to_display_dict(user, include_hash=True) if user else None


def get_user_by_whatsapp(whatsapp_number: str) -> Optional[dict]:
    init()
    with get_session() as session:
        user = session.query(User).filter(User.whatsapp_number == str(whatsapp_number)).first()
        return _to_display_dict(user, include_hash=True) if user else None


def list_users(status: Optional[str] = None, search: Optional[str] = None,
                page: int = 1, page_size: int = 20) -> dict:
    init()
    with get_session() as session:
        query = session.query(User)
        if status:
            query = query.filter(User.status == status)
        if search:
            s = f"%{search.lower()}%"
            query = query.filter(
                (User.full_name.ilike(s)) | (User.phone_number.ilike(s))
            )

        total = query.count()
        start = (page - 1) * page_size
        users = query.offset(start).limit(page_size).all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "users": [_to_display_dict(u) for u in users],
        }


def update_user(user_id: str, updates: dict, actor: str = "system") -> dict:
    init()
    field_map = {
        "Full Name": "full_name",
        "Phone Number": "phone_number",
        "WhatsApp Number": "whatsapp_number",
        "Status": "status",
        "Role": "role",
    }
    with get_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        for key, value in updates.items():
            if key in field_map:
                if key == "Status" and value not in VALID_STATUSES:
                    raise ValueError(f"Invalid status: {value}")
                if key == "Role" and value not in VALID_ROLES:
                    raise ValueError(f"Invalid role: {value}")
                setattr(user, field_map[key], value)
        user.last_activity = _now()
        session.flush()

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
    with get_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.last_activity = _now()


def set_password_hash(user_id: str, password_hash: str):
    """Used by the password reset service to set an already-hashed password directly."""
    init()
    with get_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)
        user.password_hash = password_hash


def count_users() -> dict:
    init()
    with get_session() as session:
        total = session.query(User).count()
        active = session.query(User).filter(User.status == "ACTIVE").count()
        suspended = session.query(User).filter(User.status == "SUSPENDED").count()
        today = datetime.now(timezone.utc).date().isoformat()
        new_today = session.query(User).filter(User.registration_date.like(f"{today}%")).count()
        return {"total": total, "active": active, "suspended": suspended, "new_today": new_today}
