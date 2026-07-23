"""
Analytics rollup engine (Postgres via SQLAlchemy).
Computes reports from the transactions table and persists them into
monthly_reports / spending_reports / income_reports / user_statistics.
"""
from datetime import datetime, timezone

from app.db.database import get_session, Base, engine
from app.db.models import MonthlyReport, SpendingReport, IncomeReport, UserStatistic
from app.db_engine.helpers import next_id
from app.db_engine import transactions as txn_engine
from app.db_engine import users as user_engine
from app.db_engine import logs as log_engine


def init():
    Base.metadata.create_all(
        bind=engine,
        tables=[MonthlyReport.__table__, SpendingReport.__table__, IncomeReport.__table__, UserStatistic.__table__],
    )


def _month_bounds(month_str: str) -> tuple[str, str]:
    from calendar import monthrange
    year, month = (int(x) for x in month_str.split("-"))
    last_day = monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def rollup_monthly_report(user_id: str, month_str: str, actor: str = "system") -> dict:
    init()
    date_from, date_to = _month_bounds(month_str)
    summary = txn_engine.spending_summary(user_id, date_from, date_to)

    with get_session() as session:
        existing = (
            session.query(MonthlyReport)
            .filter(MonthlyReport.user_id == user_id, MonthlyReport.month == month_str)
            .first()
        )
        if existing:
            session.delete(existing)
            session.flush()

        report_id = next_id(session, MonthlyReport, "report_id", "MREP")
        report = MonthlyReport(
            report_id=report_id,
            user_id=user_id,
            month=month_str,
            total_income=summary["total_income"],
            total_expense=summary["total_spent"],
            net=summary["total_income"] - summary["total_spent"],
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        session.add(report)
        session.flush()
        return {
            "Report ID": report.report_id, "User ID": report.user_id, "Month": report.month,
            "Total Income": report.total_income, "Total Expense": report.total_expense,
            "Net": report.net, "Generated At": report.generated_at,
        }


def rollup_spending_report(user_id: str, period_label: str, date_from: str, date_to: str) -> list[dict]:
    init()
    summary = txn_engine.spending_summary(user_id, date_from, date_to)

    with get_session() as session:
        session.query(SpendingReport).filter(
            SpendingReport.user_id == user_id, SpendingReport.period == period_label
        ).delete()
        session.flush()

        rows = []
        for category, amount in summary["by_category"].items():
            report_id = next_id(session, SpendingReport, "report_id", "SREP")
            report = SpendingReport(
                report_id=report_id, user_id=user_id, period=period_label,
                category=category, total_spent=amount,
                generated_at=datetime.now(timezone.utc).isoformat(),
            )
            session.add(report)
            session.flush()
            rows.append({
                "Report ID": report.report_id, "User ID": user_id, "Period": period_label,
                "Category": category, "Total Spent": amount, "Generated At": report.generated_at,
            })
        return rows


def rollup_income_report(user_id: str, period_label: str, date_from: str, date_to: str) -> dict:
    init()
    summary = txn_engine.spending_summary(user_id, date_from, date_to)

    with get_session() as session:
        session.query(IncomeReport).filter(
            IncomeReport.user_id == user_id, IncomeReport.period == period_label
        ).delete()
        session.flush()

        report_id = next_id(session, IncomeReport, "report_id", "IREP")
        report = IncomeReport(
            report_id=report_id, user_id=user_id, period=period_label,
            total_income=summary["total_income"], generated_at=datetime.now(timezone.utc).isoformat(),
        )
        session.add(report)
        session.flush()
        return {
            "Report ID": report.report_id, "User ID": user_id, "Period": period_label,
            "Total Income": report.total_income, "Generated At": report.generated_at,
        }


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

    with get_session() as session:
        stat = session.query(UserStatistic).filter(UserStatistic.user_id == user_id).first()
        now = datetime.now(timezone.utc).isoformat()
        if stat:
            stat.total_transactions = len(txns)
            stat.total_spent = total_spent
            stat.total_received = total_received
            stat.last_updated = now
        else:
            stat = UserStatistic(
                user_id=user_id, total_transactions=len(txns),
                total_spent=total_spent, total_received=total_received, last_updated=now,
            )
            session.add(stat)
        session.flush()
        return {
            "User ID": user_id, "Total Transactions": len(txns),
            "Total Spent": total_spent, "Total Received": total_received, "Last Updated": now,
        }


def run_full_rollup(actor: str = "system") -> dict:
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
    with get_session() as session:
        query = session.query(MonthlyReport)
        if user_id:
            query = query.filter(MonthlyReport.user_id == user_id)
        reports = query.order_by(MonthlyReport.month.desc()).limit(limit).all()
        return [{
            "Report ID": r.report_id, "User ID": r.user_id, "Month": r.month,
            "Total Income": r.total_income, "Total Expense": r.total_expense,
            "Net": r.net, "Generated At": r.generated_at,
        } for r in reports]


def get_user_statistics(user_id: str) -> dict:
    init()
    with get_session() as session:
        stat = session.query(UserStatistic).filter(UserStatistic.user_id == user_id).first()
        if not stat:
            return {}
        return {
            "User ID": stat.user_id, "Total Transactions": stat.total_transactions,
            "Total Spent": stat.total_spent, "Total Received": stat.total_received,
            "Last Updated": stat.last_updated,
        }
