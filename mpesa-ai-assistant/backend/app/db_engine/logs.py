"""
SystemLogs access layer (Postgres via SQLAlchemy).
"""
from datetime import datetime, timezone

from app.db.database import get_session, Base, engine
from app.db.models import SystemLog
from app.db_engine.helpers import next_id


def init():
    Base.metadata.create_all(bind=engine, tables=[SystemLog.__table__])


def _to_display_dict(log: SystemLog) -> dict:
    return {
        "Log ID": log.log_id,
        "Event": log.event,
        "Timestamp": log.timestamp,
        "Status": log.status,
        "Description": log.description,
        "Actor": log.actor,
    }


def log_event(event: str, status: str = "SUCCESS", description: str = "", actor: str = "system"):
    init()
    with get_session() as session:
        log_id = next_id(session, SystemLog, "log_id", "LOG")
        log = SystemLog(
            log_id=log_id,
            event=event,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            description=description,
            actor=actor,
        )
        session.add(log)
        session.flush()
        return _to_display_dict(log)


def get_recent_logs(limit: int = 100):
    init()
    with get_session() as session:
        logs = session.query(SystemLog).order_by(SystemLog.timestamp.desc()).limit(limit).all()
        return [_to_display_dict(l) for l in logs]


def get_error_logs(limit: int = 100):
    init()
    with get_session() as session:
        logs = (
            session.query(SystemLog)
            .filter(SystemLog.status == "ERROR")
            .order_by(SystemLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [_to_display_dict(l) for l in logs]
