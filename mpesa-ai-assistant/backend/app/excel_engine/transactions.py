"""
Transactions.xlsx access layer.
"""
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from app.core.config import get_settings
from app.excel_engine.base import ensure_file, read_sheet, atomic_write_sheet, append_row, next_id
from app.excel_engine import logs as log_engine
from app.excel_engine.categorization import categorize

settings = get_settings()
SHEET = "Transactions"


def init():
    ensure_file(settings.TRANSACTIONS_FILE, SHEET)


class DuplicateTransactionError(Exception):
    pass


def add_transaction(user_id: str, transaction_code: str, amount: float,
                     transaction_type: str, sender: str = "", receiver: str = "",
                     paybill_number: str = "", till_number: str = "",
                     account_reference: str = "", date: str = "", time: str = "",
                     balance: Optional[float] = None, source: str = "SMS",
                     category: Optional[str] = None) -> dict:
    init()
    df = read_sheet(settings.TRANSACTIONS_FILE, SHEET)

    # Duplicate prevention: M-Pesa transaction codes are globally unique.
    if not df.empty and transaction_code:
        if (df["Transaction Code"].astype(str) == str(transaction_code)).any():
            raise DuplicateTransactionError(f"Transaction {transaction_code} already recorded")

    if amount is None or amount < 0:
        raise ValueError("Amount must be a non-negative number")

    txn_id = next_id(df, "Transaction ID", "TXN")
    resolved_category = category or categorize(transaction_type, sender, receiver, account_reference)

    row = {
        "Transaction ID": txn_id,
        "User ID": user_id,
        "Transaction Code": transaction_code,
        "Amount": amount,
        "Transaction Type": transaction_type,
        "Sender": sender,
        "Receiver": receiver,
        "Paybill Number": paybill_number,
        "Till Number": till_number,
        "Account Reference": account_reference,
        "Date": date,
        "Time": time,
        "Category": resolved_category,
        "Balance": balance,
        "Timestamp": datetime.now(timezone.utc).isoformat(),
        "Source": source,
    }
    append_row(settings.TRANSACTIONS_FILE, SHEET, row)
    log_engine.log_event("TRANSACTION_ADDED", description=f"{txn_id} for user {user_id}: {amount}", actor=source)
    return row


def get_transaction(transaction_id: str) -> Optional[dict]:
    init()
    df = read_sheet(settings.TRANSACTIONS_FILE, SHEET)
    match = df[df["Transaction ID"] == transaction_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def list_transactions_for_user(user_id: str, limit: Optional[int] = None) -> list[dict]:
    init()
    df = read_sheet(settings.TRANSACTIONS_FILE, SHEET)
    if df.empty:
        return []
    df = df[df["User ID"] == user_id].sort_values("Timestamp", ascending=False)
    if limit:
        df = df.head(limit)
    clean_df = df.astype(object).where(df.notna(), None)
    return clean_df.to_dict(orient="records")


def search_transactions(user_id: Optional[str] = None, keyword: Optional[str] = None,
                         category: Optional[str] = None, transaction_type: Optional[str] = None,
                         date_from: Optional[str] = None, date_to: Optional[str] = None,
                         min_amount: Optional[float] = None, max_amount: Optional[float] = None,
                         page: int = 1, page_size: int = 50) -> dict:
    init()
    df = read_sheet(settings.TRANSACTIONS_FILE, SHEET)
    if df.empty:
        return {"total": 0, "page": page, "page_size": page_size, "transactions": []}

    if user_id:
        df = df[df["User ID"] == user_id]
    if category:
        df = df[df["Category"] == category]
    if transaction_type:
        df = df[df["Transaction Type"] == transaction_type]
    if keyword:
        k = keyword.lower()
        mask = (
            df["Sender"].astype(str).str.lower().str.contains(k, na=False)
            | df["Receiver"].astype(str).str.lower().str.contains(k, na=False)
            | df["Transaction Code"].astype(str).str.lower().str.contains(k, na=False)
        )
        df = df[mask]
    if date_from:
        df = df[df["Date"].astype(str) >= date_from]
    if date_to:
        df = df[df["Date"].astype(str) <= date_to]
    if min_amount is not None:
        df = df[df["Amount"] >= min_amount]
    if max_amount is not None:
        df = df[df["Amount"] <= max_amount]

    df = df.sort_values("Timestamp", ascending=False)
    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end].astype(object).where(df.iloc[start:end].notna(), None)
    return {"total": total, "page": page, "page_size": page_size, "transactions": page_df.to_dict(orient="records")}


def export_transactions(user_id: Optional[str] = None, date_from: Optional[str] = None,
                         date_to: Optional[str] = None) -> pd.DataFrame:
    """Returns a DataFrame ready to be written out as an export file."""
    result = search_transactions(user_id=user_id, date_from=date_from, date_to=date_to, page=1, page_size=1_000_000)
    return pd.DataFrame(result["transactions"])


def spending_summary(user_id: str, date_from: str, date_to: str) -> dict:
    init()
    df = read_sheet(settings.TRANSACTIONS_FILE, SHEET)
    if df.empty:
        return {"total_spent": 0, "total_income": 0, "by_category": {}, "transaction_count": 0}

    df = df[(df["User ID"] == user_id) & (df["Date"].astype(str) >= date_from) & (df["Date"].astype(str) <= date_to)]
    outgoing_types = ["SEND", "PAYBILL", "TILL", "BUY GOODS", "WITHDRAW"]
    incoming_types = ["RECEIVE", "DEPOSIT"]

    is_outgoing = df["Transaction Type"].astype(str).str.upper().apply(
        lambda t: any(o in t for o in outgoing_types))
    is_incoming = df["Transaction Type"].astype(str).str.upper().apply(
        lambda t: any(i in t for i in incoming_types))

    spent_df = df[is_outgoing]
    income_df = df[is_incoming]

    by_category = spent_df.groupby("Category")["Amount"].sum().to_dict()

    return {
        "total_spent": float(spent_df["Amount"].sum()) if not spent_df.empty else 0.0,
        "total_income": float(income_df["Amount"].sum()) if not income_df.empty else 0.0,
        "by_category": by_category,
        "transaction_count": int(len(df)),
    }


def largest_transaction(user_id: str) -> Optional[dict]:
    init()
    df = read_sheet(settings.TRANSACTIONS_FILE, SHEET)
    if df.empty:
        return None
    df = df[df["User ID"] == user_id]
    if df.empty:
        return None
    return df.loc[df["Amount"].idxmax()].to_dict()


def latest_balance(user_id: str) -> Optional[float]:
    init()
    df = read_sheet(settings.TRANSACTIONS_FILE, SHEET)
    if df.empty:
        return None
    df = df[(df["User ID"] == user_id) & (df["Balance"].notna())]
    if df.empty:
        return None
    df = df.sort_values("Timestamp", ascending=False)
    return float(df.iloc[0]["Balance"])


def system_totals() -> dict:
    init()
    df = read_sheet(settings.TRANSACTIONS_FILE, SHEET)
    if df.empty:
        return {"total_transactions": 0, "total_income": 0, "total_expenses": 0}
    outgoing_types = ["SEND", "PAYBILL", "TILL", "BUY GOODS", "WITHDRAW"]
    incoming_types = ["RECEIVE", "DEPOSIT"]
    is_outgoing = df["Transaction Type"].astype(str).str.upper().apply(lambda t: any(o in t for o in outgoing_types))
    is_incoming = df["Transaction Type"].astype(str).str.upper().apply(lambda t: any(i in t for i in incoming_types))
    return {
        "total_transactions": int(len(df)),
        "total_income": float(df[is_incoming]["Amount"].sum()) if is_incoming.any() else 0.0,
        "total_expenses": float(df[is_outgoing]["Amount"].sum()) if is_outgoing.any() else 0.0,
    }
