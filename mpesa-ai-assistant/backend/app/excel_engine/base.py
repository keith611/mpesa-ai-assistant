"""
Base Excel engine: thread-safe read/write access to .xlsx files using
pandas + openpyxl. All other excel_engine modules build on this.

Design notes:
- Each logical Excel file gets its own threading.Lock so concurrent requests
  don't corrupt the file (openpyxl is not safe for concurrent writes).
- Every write goes through `atomic_write` which writes to a temp file then
  replaces the original, so a crash mid-write never leaves a corrupt file.
- Schemas are defined once and enforced on file creation.
"""
import threading
import tempfile
import os
from pathlib import Path
from typing import Optional

import pandas as pd

from app.core.config import get_settings

settings = get_settings()

# One lock per file path, created lazily.
_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _get_lock(path: Path) -> threading.Lock:
    key = str(path)
    with _locks_guard:
        if key not in _locks:
            _locks[key] = threading.Lock()
        return _locks[key]


SCHEMAS: dict[str, list[str]] = {
    "Users": [
        "User ID", "Full Name", "Phone Number", "WhatsApp Number",
        "Password Hash", "Role", "Registration Date", "Status", "Last Activity",
    ],
    "Transactions": [
        "Transaction ID", "User ID", "Transaction Code", "Amount",
        "Transaction Type", "Sender", "Receiver", "Paybill Number",
        "Till Number", "Account Reference", "Date", "Time", "Category",
        "Balance", "Timestamp", "Source",
    ],
    "MonthlyReports": ["Report ID", "User ID", "Month", "Total Income", "Total Expense", "Net", "Generated At"],
    "SpendingReports": ["Report ID", "User ID", "Period", "Category", "Total Spent", "Generated At"],
    "IncomeReports": ["Report ID", "User ID", "Period", "Total Income", "Generated At"],
    "UserStatistics": ["User ID", "Total Transactions", "Total Spent", "Total Received", "Last Updated"],
    "SystemLogs": ["Log ID", "Event", "Timestamp", "Status", "Description", "Actor"],
    "CategoryRules": ["Rule ID", "Keyword", "Category", "Priority", "Active", "Updated By", "Updated At"],
    "AuditLogs": ["Audit ID", "Actor", "Action", "Target", "Timestamp", "IP Address", "Details"],
}


def ensure_file(path: Path, sheet_name: str):
    """Create the workbook with the correct headers if it doesn't exist yet."""
    if path.exists():
        return
    columns = SCHEMAS[sheet_name]
    df = pd.DataFrame(columns=columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def ensure_multi_sheet_file(path: Path, sheet_names: list[str]):
    """Create a workbook containing several sheets (used for Analytics.xlsx)."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name in sheet_names:
            columns = SCHEMAS[sheet_name]
            pd.DataFrame(columns=columns).to_excel(writer, sheet_name=sheet_name, index=False)


def read_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    lock = _get_lock(path)
    with lock:
        if not path.exists():
            return pd.DataFrame(columns=SCHEMAS.get(sheet_name, []))
        return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")


def atomic_write_sheet(path: Path, sheet_name: str, df: pd.DataFrame):
    """
    Write a single sheet back to disk atomically, preserving any other
    sheets already present in the workbook.
    """
    lock = _get_lock(path)
    with lock:
        all_sheets: dict[str, pd.DataFrame] = {}
        if path.exists():
            existing = pd.read_excel(path, sheet_name=None, engine="openpyxl")
            all_sheets.update(existing)
        all_sheets[sheet_name] = df

        fd, tmp_path = tempfile.mkstemp(suffix=".xlsx", dir=str(path.parent))
        os.close(fd)
        try:
            with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
                for name, sheet_df in all_sheets.items():
                    sheet_df.to_excel(writer, sheet_name=name, index=False)
            os.replace(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def append_row(path: Path, sheet_name: str, row: dict) -> pd.DataFrame:
    """Append a row (dict keyed by column name) and persist. Returns updated df."""
    df = read_sheet(path, sheet_name)
    new_row = pd.DataFrame([row])
    df = pd.concat([df, new_row], ignore_index=True)
    atomic_write_sheet(path, sheet_name, df)
    return df


def next_id(df: pd.DataFrame, id_column: str, prefix: str) -> str:
    """Generate the next sequential ID like TXN-000001."""
    if df.empty or id_column not in df.columns:
        return f"{prefix}-000001"
    existing = df[id_column].dropna().astype(str)
    numeric = existing.str.extract(r"(\d+)$")[0].dropna().astype(int)
    next_num = (numeric.max() + 1) if not numeric.empty else 1
    return f"{prefix}-{next_num:06d}"
