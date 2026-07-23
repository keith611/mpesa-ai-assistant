"""
New endpoints filling the gaps identified against the original spec:
analytics breakdowns, global search, audit log view, SMS sync / storage
status, current balance lookup, and in-app password change.

This file is entirely additive — it doesn't modify any existing route
file. The only change needed elsewhere is registering this router in
main.py (see the two-line note in the project README / chat instructions).
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.deps import get_current_claims, require_min_role
from app.core.security import verify_password, hash_password
from app.db_engine import insights
from app.db_engine import users as user_engine
from app.db_engine import transactions as txn_engine
from app.db_engine import logs as log_engine

router = APIRouter(prefix="/api/v1", tags=["Insights & Extras"])


# ---------- Analytics breakdowns ----------

def _period_bounds(period: str) -> tuple[str, str]:
    today = datetime.now(timezone.utc).date()
    if period == "weekly":
        return (today - timedelta(days=7)).isoformat(), today.isoformat()
    if period == "annual":
        return today.replace(month=1, day=1).isoformat(), today.isoformat()
    # default: monthly
    return today.replace(day=1).isoformat(), today.isoformat()


@router.get("/reports/analytics/category-breakdown", dependencies=[Depends(require_min_role("SUPPORT"))])
def category_breakdown(period: str = "monthly", user_id: str = None):
    date_from, date_to = _period_bounds(period)
    return insights.category_breakdown(date_from, date_to, user_id=user_id)


@router.get("/reports/analytics/user-growth", dependencies=[Depends(require_min_role("SUPPORT"))])
def user_growth(days: int = 30):
    return insights.user_growth(days=days)


@router.get("/reports/analytics/daily-transactions", dependencies=[Depends(require_min_role("SUPPORT"))])
def daily_transactions(days: int = 30):
    return insights.daily_transaction_counts(days=days)


@router.get("/reports/analytics/most-active-users", dependencies=[Depends(require_min_role("SUPPORT"))])
def most_active_users(limit: int = 10):
    return insights.most_active_users(limit=limit)


# ---------- Global search ----------

@router.get("/admin/search", dependencies=[Depends(require_min_role("SUPPORT"))])
def global_search(q: str = Query(..., min_length=1)):
    return insights.global_search(q)


# ---------- Audit log (admin-action view of system logs) ----------

@router.get("/admin/audit-logs", dependencies=[Depends(require_min_role("ADMIN"))])
def get_audit_logs(limit: int = 100):
    return insights.audit_logs(limit=limit)


# ---------- System monitoring extras ----------

@router.get("/reports/system/sms-sync-status", dependencies=[Depends(require_min_role("SUPPORT"))])
def sms_sync_status():
    return insights.sms_sync_status()


@router.get("/reports/system/storage-usage", dependencies=[Depends(require_min_role("SUPPORT"))])
def storage_usage():
    return insights.storage_usage()


# ---------- Current balance (used by the user profile page) ----------

@router.get("/reports/balance/{user_id}")
def current_balance(user_id: str, claims: dict = Depends(get_current_claims)):
    if claims.get("role") == "USER" and claims.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    balance = txn_engine.latest_balance(user_id)
    return {"user_id": user_id, "balance": balance}


# ---------- In-app password change (while logged in) ----------

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/auth/change-password")
def change_password(payload: ChangePasswordRequest, claims: dict = Depends(get_current_claims)):
    user_id = claims["sub"]
    user = user_engine.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(payload.current_password, user.get("Password Hash", "")):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    user_engine.set_password_hash(user_id, hash_password(payload.new_password))
    log_engine.log_event("PASSWORD_CHANGED", description=f"user={user_id}", actor=user_id)
    return {"message": "Password changed successfully."}
