"""
SystemLogs.xlsx access layer. Every significant backend event should be
logged here (login, transaction added, backup run, error, etc).
"""
from datetime import datetime, timezone

from app.core.config import get_settings
from app.excel_engine.base import ensure_file, append_row, read_sheet, next_id

settings = get_settings()
SHEET = "SystemLogs"


def init():
    ensure_file(settings.LOGS_FILE, SHEET)


def log_event(event: str, status: str = "SUCCESS", description: str = "", actor: str = "system"):
    init()
    df = read_sheet(settings.LOGS_FILE, SHEET)
    log_id = next_id(df, "Log ID", "LOG")
    row = {
        "Log ID": log_id,
        "Event": event,
        "Timestamp": datetime.now(timezone.utc).isoformat(),
        "Status": status,
        "Description": description,
        "Actor": actor,
    }
    append_row(settings.LOGS_FILE, SHEET, row)
    return row


def get_recent_logs(limit: int = 100):
    init()
    df = read_sheet(settings.LOGS_FILE, SHEET)
    if df.empty:
        return []
    return df.tail(limit).iloc[::-1].to_dict(orient="records")


def get_error_logs(limit: int = 100):
    init()
    df = read_sheet(settings.LOGS_FILE, SHEET)
    if df.empty:
        return []
    errors = df[df["Status"] == "ERROR"]
    return errors.tail(limit).iloc[::-1].to_dict(orient="records")
