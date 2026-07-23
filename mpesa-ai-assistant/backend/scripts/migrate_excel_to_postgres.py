"""
One-time migration script: imports existing data from the old Excel files
(Users.xlsx, Transactions.xlsx, Analytics.xlsx, SystemLogs.xlsx) into the
new Supabase/Postgres database.

Run once, after setting DATABASE_URL in .env and before first real use:
    python scripts/migrate_excel_to_postgres.py

Safe to re-run — it skips rows that already exist (matched by primary key),
whether they were saved in a previous run OR appear more than once within
the same Excel file (duplicate IDs are tracked in memory as each sheet is
processed, not just checked against the database, since the database
query alone won't see rows added earlier in the same unflushed batch).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import pandas as pd

from app.core.config import get_settings
from app.db.database import get_session
from app.db.models import User, Transaction, MonthlyReport, SpendingReport, IncomeReport, UserStatistic, SystemLog, CategoryRule
from app.db_engine import users as user_engine
from app.db_engine import transactions as txn_engine
from app.db_engine import analytics as analytics_engine
from app.db_engine import logs as log_engine
from app.db_engine import categorization as cat_engine

settings = get_settings()


def _clean(value):
    """Converts pandas NaN to None; leaves everything else as-is."""
    if pd.isna(value):
        return None
    return value


def _existing_ids(session, model, id_column_name):
    column = getattr(model, id_column_name)
    return {row[0] for row in session.query(column).all()}


def migrate_users(path):
    if not path.exists():
        print(f"  No {path.name} found, skipping.")
        return
    df = pd.read_excel(path, sheet_name="Users")
    user_engine.init()
    imported = 0
    skipped = 0
    with get_session() as session:
        seen = _existing_ids(session, User, "user_id")
        for _, row in df.iterrows():
            user_id = row["User ID"]
            if pd.isna(user_id) or user_id in seen:
                skipped += 1
                continue
            seen.add(user_id)
            session.add(User(
                user_id=user_id,
                full_name=_clean(row.get("Full Name")) or "",
                phone_number=str(row.get("Phone Number")),
                whatsapp_number=str(row.get("WhatsApp Number")),
                password_hash=row.get("Password Hash"),
                role=row.get("Role", "USER"),
                registration_date=str(row.get("Registration Date", "")),
                status=row.get("Status", "ACTIVE"),
                last_activity=str(row.get("Last Activity", "")),
            ))
            imported += 1
    print(f"  Users: {imported} imported, {skipped} skipped (already existed or duplicate ID)")


def migrate_transactions(path):
    if not path.exists():
        print(f"  No {path.name} found, skipping.")
        return
    df = pd.read_excel(path, sheet_name="Transactions")
    txn_engine.init()
    imported = 0
    skipped = 0
    with get_session() as session:
        seen = _existing_ids(session, Transaction, "transaction_id")
        for _, row in df.iterrows():
            txn_id = row["Transaction ID"]
            if pd.isna(txn_id) or txn_id in seen:
                skipped += 1
                continue
            seen.add(txn_id)
            session.add(Transaction(
                transaction_id=txn_id,
                user_id=row.get("User ID"),
                transaction_code=str(row.get("Transaction Code", "")),
                amount=float(row.get("Amount", 0)),
                transaction_type=row.get("Transaction Type", ""),
                sender=_clean(row.get("Sender")) or "",
                receiver=_clean(row.get("Receiver")) or "",
                paybill_number=str(_clean(row.get("Paybill Number")) or ""),
                till_number=str(_clean(row.get("Till Number")) or ""),
                account_reference=str(_clean(row.get("Account Reference")) or ""),
                date=str(_clean(row.get("Date")) or ""),
                time=str(_clean(row.get("Time")) or ""),
                category=row.get("Category", "Other"),
                balance=_clean(row.get("Balance")),
                timestamp=str(row.get("Timestamp", "")),
                source=row.get("Source", "SMS"),
            ))
            imported += 1
    print(f"  Transactions: {imported} imported, {skipped} skipped (already existed or duplicate ID)")


def migrate_analytics(path):
    if not path.exists():
        print(f"  No {path.name} found, skipping.")
        return
    analytics_engine.init()
    cat_engine.init()

    sheets = {
        "MonthlyReports": (MonthlyReport, "Report ID", "report_id"),
        "SpendingReports": (SpendingReport, "Report ID", "report_id"),
        "IncomeReports": (IncomeReport, "Report ID", "report_id"),
        "UserStatistics": (UserStatistic, "User ID", "user_id"),
        "CategoryRules": (CategoryRule, "Rule ID", "rule_id"),
    }
    for sheet_name, (model, excel_key, db_key) in sheets.items():
        try:
            df = pd.read_excel(path, sheet_name=sheet_name)
        except ValueError:
            continue
        imported = 0
        skipped = 0
        with get_session() as session:
            seen = _existing_ids(session, model, db_key)
            for _, row in df.iterrows():
                key_value = row.get(excel_key)
                if pd.isna(key_value) or key_value in seen:
                    skipped += 1
                    continue
                seen.add(key_value)
                record = {c.name: _clean(row.get(_column_to_excel_label(c.name))) for c in model.__table__.columns}
                session.add(model(**{k: v for k, v in record.items() if v is not None or k == db_key}))
                imported += 1
        print(f"  {sheet_name}: {imported} imported, {skipped} skipped (already existed or duplicate ID)")


def _column_to_excel_label(column_name):
    overrides = {
        "report_id": "Report ID", "user_id": "User ID", "rule_id": "Rule ID",
        "total_income": "Total Income", "total_expense": "Total Expense", "net": "Net",
        "generated_at": "Generated At", "period": "Period", "category": "Category",
        "total_spent": "Total Spent", "total_transactions": "Total Transactions",
        "total_received": "Total Received", "last_updated": "Last Updated",
        "keyword": "Keyword", "priority": "Priority", "active": "Active",
        "updated_by": "Updated By", "updated_at": "Updated At", "month": "Month",
    }
    return overrides.get(column_name, column_name)


def migrate_logs(path):
    if not path.exists():
        print(f"  No {path.name} found, skipping.")
        return
    df = pd.read_excel(path, sheet_name="SystemLogs")
    log_engine.init()
    imported = 0
    skipped = 0
    with get_session() as session:
        seen = _existing_ids(session, SystemLog, "log_id")
        for _, row in df.iterrows():
            log_id = row.get("Log ID")
            if pd.isna(log_id) or log_id in seen:
                skipped += 1
                continue
            seen.add(log_id)
            session.add(SystemLog(
                log_id=log_id,
                event=row.get("Event", ""),
                timestamp=str(row.get("Timestamp", "")),
                status=row.get("Status", "SUCCESS"),
                description=_clean(row.get("Description")) or "",
                actor=row.get("Actor", "system"),
            ))
            imported += 1
    print(f"  SystemLogs: {imported} imported, {skipped} skipped (already existed or duplicate ID)")


def main():
    if not settings.DATABASE_URL:
        print("DATABASE_URL is not set in .env — set it first, then re-run this script.")
        return

    data_dir = settings.DATA_DIR
    print(f"Migrating Excel data from {data_dir} into Postgres...\n")

    print("Users.xlsx:")
    migrate_users(data_dir / "Users.xlsx")

    print("\nTransactions.xlsx:")
    migrate_transactions(data_dir / "Transactions.xlsx")

    print("\nAnalytics.xlsx:")
    migrate_analytics(data_dir / "Analytics.xlsx")

    print("\nSystemLogs.xlsx:")
    migrate_logs(data_dir / "SystemLogs.xlsx")

    print("\nMigration complete.")


if __name__ == "__main__":
    main()