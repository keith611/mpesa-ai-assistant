"""
Transactions table access layer (Postgres via SQLAlchemy).
"""
from datetime import datetime, timezone
from typing import Optional

from app.db.database import get_session, Base, engine
from app.db.models import Transaction
from app.db_engine.helpers import next_id
from app.db_engine import logs as log_engine
from app.db_engine.categorization import categorize

OUTGOING_TYPES = ["SEND", "PAYBILL", "TILL", "BUY GOODS", "WITHDRAW"]
INCOMING_TYPES = ["RECEIVE", "DEPOSIT"]


class DuplicateTransactionError(Exception):
    pass


def init():
    Base.metadata.create_all(bind=engine, tables=[Transaction.__table__])


def _to_display_dict(t):
    return {
        "Transaction ID": t.transaction_id,
        "User ID": t.user_id,
        "Transaction Code": t.transaction_code,
        "Amount": t.amount,
        "Transaction Type": t.transaction_type,
        "Sender": t.sender,
        "Receiver": t.receiver,
        "Paybill Number": t.paybill_number,
        "Till Number": t.till_number,
        "Account Reference": t.account_reference,
        "Date": t.date,
        "Time": t.time,
        "Category": t.category,
        "Balance": t.balance,
        "Timestamp": t.timestamp,
        "Source": t.source,
    }


def add_transaction(user_id, transaction_code, amount,
                     transaction_type, sender="", receiver="",
                     paybill_number="", till_number="",
                     account_reference="", date="", time="",
                     balance=None, source="SMS",
                     category=None):
    init()
    if amount is None or amount < 0:
        raise ValueError("Amount must be a non-negative number")

    with get_session() as session:
        if transaction_code:
            existing = session.query(Transaction).filter(Transaction.transaction_code == str(transaction_code)).first()
            if existing:
                raise DuplicateTransactionError(f"Transaction {transaction_code} already recorded")

        txn_id = next_id(session, Transaction, "transaction_id", "TXN")
        resolved_category = category or categorize(transaction_type, sender, receiver, account_reference)

        txn = Transaction(
            transaction_id=txn_id,
            user_id=user_id,
            transaction_code=transaction_code,
            amount=amount,
            transaction_type=transaction_type,
            sender=sender,
            receiver=receiver,
            paybill_number=paybill_number,
            till_number=till_number,
            account_reference=account_reference,
            date=date,
            time=time,
            category=resolved_category,
            balance=balance,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source=source,
        )
        session.add(txn)
        session.flush()
        result = _to_display_dict(txn)

    log_engine.log_event("TRANSACTION_ADDED", description=f"{txn_id} for user {user_id}: {amount}", actor=source)
    return result


def get_transaction(transaction_id):
    init()
    with get_session() as session:
        txn = session.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        return _to_display_dict(txn) if txn else None


def list_transactions_for_user(user_id, limit=None):
    init()
    with get_session() as session:
        query = session.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.timestamp.desc())
        if limit:
            query = query.limit(limit)
        return [_to_display_dict(t) for t in query.all()]


def search_transactions(user_id=None, keyword=None,
                         category=None, transaction_type=None,
                         date_from=None, date_to=None,
                         min_amount=None, max_amount=None,
                         page=1, page_size=50):
    init()
    with get_session() as session:
        query = session.query(Transaction)
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        if category:
            query = query.filter(Transaction.category == category)
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        if keyword:
            k = f"%{keyword.lower()}%"
            query = query.filter(
                (Transaction.sender.ilike(k)) | (Transaction.receiver.ilike(k)) | (Transaction.transaction_code.ilike(k))
            )
        if date_from:
            query = query.filter(Transaction.date >= date_from)
        if date_to:
            query = query.filter(Transaction.date <= date_to)
        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)
        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)

        total = query.count()
        query = query.order_by(Transaction.timestamp.desc())
        start = (page - 1) * page_size
        transactions = query.offset(start).limit(page_size).all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "transactions": [_to_display_dict(t) for t in transactions],
        }


def export_transactions(user_id=None, date_from=None, date_to=None):
    import pandas as pd
    result = search_transactions(user_id=user_id, date_from=date_from, date_to=date_to, page=1, page_size=1_000_000)
    return pd.DataFrame(result["transactions"])


def spending_summary(user_id, date_from, date_to):
    init()
    total_spent = 0.0
    total_income = 0.0
    by_category = {}
    transaction_count = 0

    with get_session() as session:
        transactions = (
            session.query(Transaction)
            .filter(Transaction.user_id == user_id, Transaction.date >= date_from, Transaction.date <= date_to)
            .all()
        )
        transaction_count = len(transactions)

        for t in transactions:
            ttype = (t.transaction_type or "").upper()
            if any(o in ttype for o in OUTGOING_TYPES):
                total_spent += t.amount
                by_category[t.category] = by_category.get(t.category, 0) + t.amount
            elif any(i in ttype for i in INCOMING_TYPES):
                total_income += t.amount

    return {
        "total_spent": total_spent,
        "total_income": total_income,
        "by_category": by_category,
        "transaction_count": transaction_count,
    }


def largest_transaction(user_id):
    init()
    with get_session() as session:
        txn = (
            session.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.amount.desc())
            .first()
        )
        return _to_display_dict(txn) if txn else None


def latest_balance(user_id):
    init()
    with get_session() as session:
        txn = (
            session.query(Transaction)
            .filter(Transaction.user_id == user_id, Transaction.balance.isnot(None))
            .order_by(Transaction.timestamp.desc())
            .first()
        )
        return txn.balance if txn else None


def system_totals():
    init()
    total_income = 0.0
    total_expenses = 0.0
    total_transactions = 0

    with get_session() as session:
        transactions = session.query(Transaction).all()
        total_transactions = len(transactions)

        for t in transactions:
            ttype = (t.transaction_type or "").upper()
            if any(o in ttype for o in OUTGOING_TYPES):
                total_expenses += t.amount
            elif any(i in ttype for i in INCOMING_TYPES):
                total_income += t.amount

    return {"total_transactions": total_transactions, "total_income": total_income, "total_expenses": total_expenses}