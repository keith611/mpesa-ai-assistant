"""
Backup system, adapted for Postgres.

Supabase already backs up the actual database at the infrastructure level
on paid plans (point-in-time recovery). This module provides a
lighter-weight, application-level snapshot on top of that: it exports
every table to CSV files under backups/{tier}/{timestamp}/, which the
admin dashboard's existing Backup Management page can list, validate,
and restore from — useful for quick point-in-time exports you can
inspect or archive independently of Supabase's own backup system.
"""
import shutil
import csv
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from app.core.config import get_settings
from app.db.database import get_session
from app.db.models import User, Transaction, MonthlyReport, SpendingReport, IncomeReport, UserStatistic, SystemLog, CategoryRule
from app.db_engine import logs as log_engine

settings = get_settings()

TABLES = {
    "Users.csv": User,
    "Transactions.csv": Transaction,
    "MonthlyReports.csv": MonthlyReport,
    "SpendingReports.csv": SpendingReport,
    "IncomeReports.csv": IncomeReport,
    "UserStatistics.csv": UserStatistic,
    "SystemLogs.csv": SystemLog,
    "CategoryRules.csv": CategoryRule,
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def run_backup(tier: str) -> dict:
    if tier not in ("hourly", "daily", "weekly"):
        raise ValueError("tier must be hourly, daily, or weekly")

    dest_dir = settings.BACKUP_DIR / tier / _timestamp()
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    with get_session() as session:
        for filename, model in TABLES.items():
            rows = session.query(model).all()
            if not rows:
                # Still write an empty file with headers so validate/restore see a consistent shape.
                columns = [c.name for c in model.__table__.columns]
                pd.DataFrame(columns=columns).to_csv(dest_dir / filename, index=False)
            else:
                records = [{c.name: getattr(r, c.name) for c in model.__table__.columns} for r in rows]
                pd.DataFrame(records).to_csv(dest_dir / filename, index=False)
            copied.append(filename)

    _prune(tier)
    log_engine.log_event("BACKUP_RUN", description=f"{tier} backup created at {dest_dir.name} ({len(copied)} tables)")
    return {"tier": tier, "path": str(dest_dir), "files": copied, "timestamp": dest_dir.name}


def _prune(tier: str):
    limits = {
        "hourly": settings.HOURLY_BACKUPS_TO_KEEP,
        "daily": settings.DAILY_BACKUPS_TO_KEEP,
        "weekly": settings.WEEKLY_BACKUPS_TO_KEEP,
    }
    tier_dir = settings.BACKUP_DIR / tier
    if not tier_dir.exists():
        return
    snapshots = sorted([p for p in tier_dir.iterdir() if p.is_dir()], key=lambda p: p.name)
    excess = len(snapshots) - limits[tier]
    for old in snapshots[:max(excess, 0)]:
        shutil.rmtree(old, ignore_errors=True)


def list_backups(tier: str = None) -> list[dict]:
    tiers = [tier] if tier else ["hourly", "daily", "weekly"]
    results = []
    for t in tiers:
        tier_dir = settings.BACKUP_DIR / t
        if not tier_dir.exists():
            continue
        for snap in sorted(tier_dir.iterdir(), reverse=True):
            if snap.is_dir():
                files = [f.name for f in snap.iterdir()]
                results.append({
                    "tier": t,
                    "snapshot": snap.name,
                    "path": str(snap),
                    "files": files,
                    "size_bytes": sum(f.stat().st_size for f in snap.iterdir() if f.is_file()),
                })
    return results


def validate_backup(tier: str, snapshot: str) -> dict:
    snap_dir = settings.BACKUP_DIR / tier / snapshot
    if not snap_dir.exists():
        return {"valid": False, "reason": "snapshot not found"}

    issues = []
    for filename in TABLES:
        f = snap_dir / filename
        if not f.exists():
            issues.append(f"{filename} missing")
            continue
        try:
            pd.read_csv(f)
        except Exception as e:
            issues.append(f"{filename} unreadable: {e}")

    return {"valid": len(issues) == 0, "issues": issues}


def restore_backup(tier: str, snapshot: str, actor: str = "admin") -> dict:
    """
    Restores from a CSV snapshot by truncating and reloading each table.
    A safety snapshot of the CURRENT state is taken first so this is
    reversible if something goes wrong.
    """
    validation = validate_backup(tier, snapshot)
    if not validation["valid"]:
        raise ValueError(f"Cannot restore invalid backup: {validation['issues']}")

    run_backup("hourly")  # safety net before overwriting

    snap_dir = settings.BACKUP_DIR / tier / snapshot
    restored = []
    with get_session() as session:
        for filename, model in TABLES.items():
            df = pd.read_csv(snap_dir / filename)
            session.query(model).delete()
            session.flush()
            if not df.empty:
                # Convert NaN back to None for nullable columns (e.g. Transaction.balance).
                records = df.where(pd.notna(df), None).to_dict(orient="records")
                session.bulk_insert_mappings(model, records)
            restored.append(filename)

    log_engine.log_event("BACKUP_RESTORED", description=f"Restored from {tier}/{snapshot}: {restored}", actor=actor)
    return {"restored_files": restored, "from": f"{tier}/{snapshot}"}
