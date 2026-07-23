"""
Analytics rollup engine.

Computes reports from Transactions.xlsx and persists them into
Analytics.xlsx's MonthlyReports / SpendingReports / IncomeReports /
UserStatistics sheets. This gives the admin dashboard a fast, pre-computed
source to read from instead of recomputing from raw transactions every
time, and gives us a historical record of past reports.

Rollups are triggered:
  - automatically, monthly, by the scheduler (see services/scheduler.py)
  - on demand, by an admin, via POST /api/v1/reports/rollup
"""
from datetime import datetime, timezone
from calendar import monthrange

import pandas as pd

from app.core.config import get_settings
from app.excel_engine.base import ensure_multi_sheet_file, read_sheet, atomic_write_sheet, next_id
from app.excel_engine import transactions as txn_engine
from app.excel_engine import users as user_engine
from app.excel_engine import logs as log_engine
from app.excel_engine.categorization import ANALYTICS_SHEETS, RULES_SHEET

settings = get_settings()

ALL_SHEETS = ANALYTICS_SHEETS + [RULES_SHEET]


def init():
    ensure_multi_sheet_file(settings.ANALYTICS_FILE, ALL_SHEETS)


def _month_bounds(month_str: str) -> tuple[str, str]:
    """month_str format: 'YYYY-MM'. Returns (first_day, last_day) as ISO date strings."""
    year, month = (int(x) for x in month_str.split("-"))
    last_day = monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def rollup_monthly_report(user_id: str, month_str: str, actor: str = "system") -> dict:
    init()
    date_from, date_to = _month_bounds(month_str)
    summary = txn_engine.spending_summary(user_id, date_from, date_to)

    df = read_sheet(settings.ANALYTICS_FILE, "MonthlyReports")
    # Remove any previous rollup for the same user+month so re-running is idempotent.
    if not df.empty:
        df = df[~((df["User ID"] == user_id) & (df["Month"] == month_str))]

    report_id = next_id(df, "Report ID", "MREP")
    row = {
        "Report ID": report_id,
        "User ID": user_id,
        "Month": month_str,
        "Total Income": summary["total_income"],
        "Total Expense": summary["total_spent"],
        "Net": summary["total_income"] - summary["total_spent"],
        "Generated At": datetime.now(timezone.utc).isoformat(),
    }
    new_row = pd.DataFrame([row])
    df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
    atomic_write_sheet(settings.ANALYTICS_FILE, "MonthlyReports", df)
    return row


def rollup_spending_report(user_id: str, period_label: str, date_from: str, date_to: str) -> list[dict]:
    init()
    summary = txn_engine.spending_summary(user_id, date_from, date_to)

    df = read_sheet(settings.ANALYTICS_FILE, "SpendingReports")
    if not df.empty:
        df = df[~((df["User ID"] == user_id) & (df["Period"] == period_label))]

    rows = []
    for category, amount in summary["by_category"].items():
        report_id = next_id(df, "Report ID", "SREP") if df.empty else f"SREP-{len(df) + len(rows) + 1:06d}"
        rows.append({
            "Report ID": report_id,
            "User ID": user_id,
            "Period": period_label,
            "Category": category,
            "Total Spent": amount,
            "Generated At": datetime.now(timezone.utc).isoformat(),
        })

    if rows:
        new_rows = pd.DataFrame(rows)
        df = pd.concat([df, new_rows], ignore_index=True) if not df.empty else new_rows
        atomic_write_sheet(settings.ANALYTICS_FILE, "SpendingReports", df)
    return rows


def rollup_income_report(user_id: str, period_label: str, date_from: str, date_to: str) -> dict:
    init()
    summary = txn_engine.spending_summary(user_id, date_from, date_to)

    df = read_sheet(settings.ANALYTICS_FILE, "IncomeReports")
    if not df.empty:
        df = df[~((df["User ID"] == user_id) & (df["Period"] == period_label))]

    report_id = next_id(df, "Report ID", "IREP")
    row = {
        "Report ID": report_id,
        "User ID": user_id,
        "Period": period_label,
        "Total Income": summary["total_income"],
        "Generated At": datetime.now(timezone.utc).isoformat(),
    }
    new_row = pd.DataFrame([row])
    df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
    atomic_write_sheet(settings.ANALYTICS_FILE, "IncomeReports", df)
    return row


def update_user_statistics(user_id: str) -> dict:
    init()
    txns = txn_engine.list_transactions_for_user(user_id)
    outgoing_types = ["SEND", "PAYBILL", "TILL", "BUY GOODS", "WITHDRAW"]
    incoming_types = ["RECEIVE", "DEPOSIT"]

    total_spent = sum(
        t["Amount"] for t in txns
        if any(o in str(t.get("Transaction Type", "")).upper() for o in outgoing_types)
    )
    total_received = sum(
        t["Amount"] for t in txns
        if any(i in str(t.get("Transaction Type", "")).upper() for i in incoming_types)
    )

    df = read_sheet(settings.ANALYTICS_FILE, "UserStatistics")
    row = {
        "User ID": user_id,
        "Total Transactions": len(txns),
        "Total Spent": total_spent,
        "Total Received": total_received,
        "Last Updated": datetime.now(timezone.utc).isoformat(),
    }

    if not df.empty and (df["User ID"] == user_id).any():
        idx = df.index[df["User ID"] == user_id]
        for key, value in row.items():
            df.loc[idx, key] = value
    else:
        new_row = pd.DataFrame([row])
        df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row

    atomic_write_sheet(settings.ANALYTICS_FILE, "UserStatistics", df)
    return row


def run_full_rollup(actor: str = "system") -> dict:
    """
    Rolls up the current month for every active user: MonthlyReports,
    SpendingReports, IncomeReports, UserStatistics. Called by the
    scheduler on the 1st of each month, and available on-demand for admins.
    """
    init()
    today = datetime.now(timezone.utc).date()
    month_str = today.strftime("%Y-%m")
    date_from = today.replace(day=1).isoformat()
    date_to = today.isoformat()

    all_users = user_engine.list_users(page=1, page_size=1_000_000)["users"]
    processed = 0
    for user in all_users:
        user_id = user["User ID"]
        rollup_monthly_report(user_id, month_str, actor=actor)
        rollup_spending_report(user_id, f"monthly:{month_str}", date_from, date_to)
        rollup_income_report(user_id, f"monthly:{month_str}", date_from, date_to)
        update_user_statistics(user_id)
        processed += 1

    log_engine.log_event("ANALYTICS_ROLLUP", description=f"Rolled up {processed} users for {month_str}", actor=actor)
    return {"users_processed": processed, "month": month_str}


def get_monthly_reports(user_id: str = None, limit: int = 24) -> list[dict]:
    init()
    df = read_sheet(settings.ANALYTICS_FILE, "MonthlyReports")
    if df.empty:
        return []
    if user_id:
        df = df[df["User ID"] == user_id]
    result_df = df.sort_values("Month", ascending=False).head(limit)
    result_df = result_df.astype(object).where(result_df.notna(), None)
    return result_df.to_dict(orient="records")


def get_user_statistics(user_id: str) -> dict:
    init()
    df = read_sheet(settings.ANALYTICS_FILE, "UserStatistics")
    if df.empty:
        return {}
    match = df[df["User ID"] == user_id]
    if match.empty:
        return {}
    return match.iloc[0].to_dict()
