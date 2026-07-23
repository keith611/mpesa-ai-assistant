"""
ORM models. Column names are chosen to match the original Excel column
names in spirit (e.g. "Full Name" -> full_name) so the mapping is easy to
follow, but use standard snake_case since Postgres doesn't need the
spaces-in-column-names Excel required.

Dates/times that were plain strings in the Excel version (e.g. "2026-07-09")
stay as TEXT columns here rather than DATE/TIME, so all the existing
string-comparison logic ported from the Excel engine (df["Date"] >= x)
continues to work identically as SQL string comparisons, which are safe
for ISO 8601 formatted dates.
"""
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Text
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column("user_id", String, primary_key=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    whatsapp_number = Column(String, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="USER")
    registration_date = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    last_activity = Column(String, nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    transaction_code = Column(String, unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    sender = Column(String, default="")
    receiver = Column(String, default="")
    paybill_number = Column(String, default="")
    till_number = Column(String, default="")
    account_reference = Column(String, default="")
    date = Column(String, default="", index=True)
    time = Column(String, default="")
    category = Column(String, default="Other")
    balance = Column(Float, nullable=True)
    timestamp = Column(String, nullable=False, index=True)
    source = Column(String, default="SMS")


class MonthlyReport(Base):
    __tablename__ = "monthly_reports"

    report_id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    month = Column(String, nullable=False, index=True)
    total_income = Column(Float, default=0)
    total_expense = Column(Float, default=0)
    net = Column(Float, default=0)
    generated_at = Column(String, nullable=False)


class SpendingReport(Base):
    __tablename__ = "spending_reports"

    report_id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    period = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)
    total_spent = Column(Float, default=0)
    generated_at = Column(String, nullable=False)


class IncomeReport(Base):
    __tablename__ = "income_reports"

    report_id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    period = Column(String, nullable=False, index=True)
    total_income = Column(Float, default=0)
    generated_at = Column(String, nullable=False)


class UserStatistic(Base):
    __tablename__ = "user_statistics"

    user_id = Column(String, primary_key=True)
    total_transactions = Column(Integer, default=0)
    total_spent = Column(Float, default=0)
    total_received = Column(Float, default=0)
    last_updated = Column(String, nullable=False)


class SystemLog(Base):
    __tablename__ = "system_logs"

    log_id = Column(String, primary_key=True)
    event = Column(String, nullable=False)
    timestamp = Column(String, nullable=False, index=True)
    status = Column(String, default="SUCCESS")
    description = Column(Text, default="")
    actor = Column(String, default="system")


class CategoryRule(Base):
    __tablename__ = "category_rules"

    rule_id = Column(String, primary_key=True)
    keyword = Column(String, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(Integer, default=5)
    active = Column(Boolean, default=True)
    updated_by = Column(String, default="system")
    updated_at = Column(String, nullable=False)
