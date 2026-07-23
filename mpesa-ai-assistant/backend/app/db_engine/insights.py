"""
New, additive query module: analytics breakdowns, global search, and
audit-log filtering. Does not modify any existing table or existing
db_engine module — reads from the same users/transactions/system_logs
tables that already exist.
"""
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from app.db.database import get_session
from app.db.models import User, Transaction, SystemLog

OUTGOING_TYPES = ["SEND", "PAYBILL", "TILL", "BUY GOODS", "WITHDRAW"]
INCOMING_TYPES = ["RECEIVE", "DEPOSIT"]

# Actors that represent the system itself, not a real admin/user action —
# excluded from the audit log view so it only shows genuine human actions.
SYSTEM_ACTORS = {"system", "scheduler", "whatsapp_mock", "whatsapp_live"}


def category_breakdown(date_from: str, date_to: str, user_id: str = None) -> list[dict]:
    """Spending grouped by category across the given period (all users, or one)."""
    with get_session() as session:
        query = session.query(Transaction).filter(
            Transaction.date >= date_from, Transaction.date <= date_to
        )
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        transactions = query.all()

        totals: dict[str, float] = defaultdict(float)
        for t in transactions:
            ttype = (t.transaction_type or "").upper()
            if any(o in ttype for o in OUTGOING_TYPES):
                totals[t.category or "Other"] += t.amount

    return [{"category": cat, "amount": amt} for cat, amt in sorted(totals.items(), key=lambda x: -x[1])]


def user_growth(days: int = 30) -> list[dict]:
    """New user registrations per day over the last N days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    with get_session() as session:
        users = session.query(User.registration_date).filter(User.registration_date >= cutoff).all()

        counts: dict[str, int] = defaultdict(int)
        for (reg_date,) in users:
            day = (reg_date or "")[:10]
            if day:
                counts[day] += 1

    return [{"date": d, "new_users": c} for d, c in sorted(counts.items())]


def daily_transaction_counts(days: int = 30) -> list[dict]:
    """Transaction count per day over the last N days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    with get_session() as session:
        transactions = session.query(Transaction.date).filter(Transaction.date >= cutoff).all()

        counts: dict[str, int] = defaultdict(int)
        for (date,) in transactions:
            if date:
                counts[date] += 1

    return [{"date": d, "transaction_count": c} for d, c in sorted(counts.items())]


def most_active_users(limit: int = 10) -> list[dict]:
    """Top users ranked by transaction count."""
    with get_session() as session:
        transactions = session.query(Transaction.user_id).all()
        users_by_id = {u.user_id: u.full_name for u in session.query(User).all()}

        counts: dict[str, int] = defaultdict(int)
        for (user_id,) in transactions:
            counts[user_id] += 1

    ranked = sorted(counts.items(), key=lambda x: -x[1])[:limit]
    return [
        {"user_id": uid, "full_name": users_by_id.get(uid, uid), "transaction_count": count}
        for uid, count in ranked
    ]


def global_search(query_text: str, limit: int = 20) -> dict:
    """Searches users and transactions together for the admin dashboard's search bar."""
    q = f"%{query_text.lower()}%"
    with get_session() as session:
        matched_users = (
            session.query(User)
            .filter(
                (User.full_name.ilike(q))
                | (User.phone_number.ilike(q))
                | (User.whatsapp_number.ilike(q))
                | (User.user_id.ilike(q))
            )
            .limit(limit)
            .all()
        )
        users_result = [
            {
                "User ID": u.user_id, "Full Name": u.full_name, "Phone Number": u.phone_number,
                "WhatsApp Number": u.whatsapp_number, "Status": u.status,
            }
            for u in matched_users
        ]

        txn_filters = (
            (Transaction.transaction_code.ilike(q))
            | (Transaction.sender.ilike(q))
            | (Transaction.receiver.ilike(q))
            | (Transaction.category.ilike(q))
            | (Transaction.user_id.ilike(q))
        )
        # If the search text parses as a number, also match on exact amount.
        try:
            amount_value = float(query_text)
            txn_filters = txn_filters | (Transaction.amount == amount_value)
        except ValueError:
            pass

        matched_txns = session.query(Transaction).filter(txn_filters).limit(limit).all()
        transactions_result = [
            {
                "Transaction ID": t.transaction_id, "User ID": t.user_id,
                "Transaction Code": t.transaction_code, "Amount": t.amount,
                "Transaction Type": t.transaction_type, "Sender": t.sender,
                "Receiver": t.receiver, "Category": t.category, "Date": t.date,
            }
            for t in matched_txns
        ]

    return {"users": users_result, "transactions": transactions_result}


def audit_logs(limit: int = 100) -> list[dict]:
    """System logs filtered down to genuine admin/user actions (excludes automated system events)."""
    with get_session() as session:
        logs = session.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(limit * 3).all()
        filtered = [l for l in logs if l.actor not in SYSTEM_ACTORS][:limit]
        return [
            {
                "Log ID": l.log_id, "Event": l.event, "Timestamp": l.timestamp,
                "Status": l.status, "Description": l.description, "Actor": l.actor,
            }
            for l in filtered
        ]


def sms_sync_status() -> dict:
    """Last time an SMS-sourced transaction was ingested, and how many arrived today."""
    today = datetime.now(timezone.utc).date().isoformat()
    with get_session() as session:
        latest = (
            session.query(Transaction)
            .filter(Transaction.source == "SMS")
            .order_by(Transaction.timestamp.desc())
            .first()
        )
        today_count = (
            session.query(Transaction)
            .filter(Transaction.source == "SMS", Transaction.timestamp.like(f"{today}%"))
            .count()
        )
    return {
        "last_sms_received_at": latest.timestamp if latest else None,
        "synced_today": today_count,
    }


def storage_usage() -> dict:
    """Row counts across the main tables — a Postgres-era stand-in for the old 'Excel file size' metric."""
    with get_session() as session:
        return {
            "users": session.query(User).count(),
            "transactions": session.query(Transaction).count(),
            "system_logs": session.query(SystemLog).count(),
        }
