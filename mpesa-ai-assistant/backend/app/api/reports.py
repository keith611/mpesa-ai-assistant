"""
Reports and analytics endpoints (Admin dashboard's Overview/Analytics/Reports pages).
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import io

from app.core.deps import get_current_claims, require_min_role
from app.db_engine import transactions as txn_engine
from app.db_engine import users as user_engine
from app.db_engine import logs as log_engine
from app.db_engine import analytics as analytics_engine
from app.services import report_generator

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

PERIODS = {"daily", "weekly", "monthly", "annual"}


def _today_str():
    return datetime.now(timezone.utc).date().isoformat()


def _period_bounds(period: str) -> tuple[str, str]:
    today = datetime.now(timezone.utc).date()
    if period == "daily":
        return today.isoformat(), today.isoformat()
    if period == "weekly":
        return (today - timedelta(days=today.weekday())).isoformat(), today.isoformat()
    if period == "monthly":
        return today.replace(day=1).isoformat(), today.isoformat()
    if period == "annual":
        return today.replace(month=1, day=1).isoformat(), today.isoformat()
    raise ValueError(f"Unknown period: {period}. Must be one of {PERIODS}")


def _authorize_user_access(claims: dict, user_id: str):
    if claims.get("role") == "USER" and claims.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's reports")


@router.get("/overview", dependencies=[Depends(require_min_role("SUPPORT"))])
def overview():
    user_counts = user_engine.count_users()
    txn_totals = txn_engine.system_totals()
    return {
        "total_users": user_counts["total"],
        "active_users": user_counts["active"],
        "new_users_today": user_counts["new_today"],
        "total_transactions": txn_totals["total_transactions"],
        "total_income": txn_totals["total_income"],
        "total_expenses": txn_totals["total_expenses"],
    }


# ---------- Daily / Weekly / Monthly / Annual reports (per spec section: Reports) ----------

@router.get("/{period}/{user_id}")
def period_report(period: str, user_id: str, claims: dict = Depends(get_current_claims)):
    """period is one of: daily, weekly, monthly, annual"""
    _authorize_user_access(claims, user_id)
    if period not in PERIODS:
        raise HTTPException(status_code=400, detail=f"period must be one of {sorted(PERIODS)}")
    date_from, date_to = _period_bounds(period)
    summary = txn_engine.spending_summary(user_id, date_from, date_to)
    return {"period": period, "date_from": date_from, "date_to": date_to, **summary}


@router.get("/spending/{user_id}")
def spending_report(user_id: str, period: str = "monthly", claims: dict = Depends(get_current_claims)):
    _authorize_user_access(claims, user_id)
    date_from, date_to = _period_bounds(period if period in PERIODS else "monthly")
    return txn_engine.spending_summary(user_id, date_from=date_from, date_to=date_to)


@router.get("/user-activity/{user_id}")
def user_activity(user_id: str, claims: dict = Depends(require_min_role("SUPPORT"))):
    txns = txn_engine.list_transactions_for_user(user_id, limit=20)
    user = user_engine.get_user_by_id(user_id)
    stats = analytics_engine.get_user_statistics(user_id)
    return {
        "user": {k: v for k, v in (user or {}).items() if k != "Password Hash"},
        "recent_transactions": txns,
        "statistics": stats,
    }


# ---------- Downloadable reports: PDF and Excel ----------

@router.get("/download/pdf/{user_id}")
def download_pdf_report(user_id: str, period: str = "monthly", claims: dict = Depends(get_current_claims)):
    _authorize_user_access(claims, user_id)
    date_from, date_to = _period_bounds(period if period in PERIODS else "monthly")
    pdf_bytes = report_generator.build_pdf_report(user_id, date_from, date_to)
    filename = f"statement_{user_id}_{period}_{_today_str()}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes), media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/download/excel/{user_id}")
def download_excel_report(user_id: str, period: str = "monthly", claims: dict = Depends(get_current_claims)):
    _authorize_user_access(claims, user_id)
    date_from, date_to = _period_bounds(period if period in PERIODS else "monthly")
    xlsx_bytes = report_generator.build_excel_report(user_id, date_from, date_to)
    filename = f"statement_{user_id}_{period}_{_today_str()}.xlsx"
    return StreamingResponse(
        io.BytesIO(xlsx_bytes), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------- Analytics rollups (persisted into Analytics.xlsx) ----------

@router.post("/rollup", dependencies=[Depends(require_min_role("ADMIN"))])
def trigger_rollup(claims: dict = Depends(get_current_claims)):
    """Manually trigger the monthly analytics rollup (also runs automatically via scheduler)."""
    return analytics_engine.run_full_rollup(actor=claims["sub"])


@router.get("/monthly-history/{user_id}")
def monthly_history(user_id: str, claims: dict = Depends(get_current_claims)):
    _authorize_user_access(claims, user_id)
    return analytics_engine.get_monthly_reports(user_id=user_id)


@router.get("/monthly-history", dependencies=[Depends(require_min_role("SUPPORT"))])
def monthly_history_all():
    return analytics_engine.get_monthly_reports()


@router.get("/statistics/{user_id}")
def user_statistics(user_id: str, claims: dict = Depends(get_current_claims)):
    _authorize_user_access(claims, user_id)
    return analytics_engine.get_user_statistics(user_id)


# ---------- System logs ----------

@router.get("/system/logs", dependencies=[Depends(require_min_role("ADMIN"))])
def system_logs(limit: int = 100):
    return log_engine.get_recent_logs(limit=limit)


@router.get("/system/errors", dependencies=[Depends(require_min_role("ADMIN"))])
def system_errors(limit: int = 100):
    return log_engine.get_error_logs(limit=limit)
