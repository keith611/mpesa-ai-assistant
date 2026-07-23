"""
Backup system for all Excel data files.

Copies Users.xlsx, Transactions.xlsx, Analytics.xlsx, SystemLogs.xlsx into
timestamped folders under backups/{hourly,daily,weekly}/, and prunes old
backups beyond the configured retention.

Intended to be triggered by a scheduler (see app/services/scheduler.py)
but also exposed as functions the admin dashboard can call on demand.
"""
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings
from app.excel_engine import logs as log_engine

settings = get_settings()

DATA_FILES = ["Users.xlsx", "Transactions.xlsx", "Analytics.xlsx", "SystemLogs.xlsx"]


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def run_backup(tier: str) -> dict:
    """tier is one of 'hourly', 'daily', 'weekly'."""
    if tier not in ("hourly", "daily", "weekly"):
        raise ValueError("tier must be hourly, daily, or weekly")

    dest_dir = settings.BACKUP_DIR / tier / _timestamp()
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for filename in DATA_FILES:
        src = settings.DATA_DIR / filename
        if src.exists():
            dst = dest_dir / filename
            shutil.copy2(src, dst)
            copied.append(filename)

    _prune(tier)
    log_engine.log_event("BACKUP_RUN", description=f"{tier} backup created at {dest_dir.name} ({len(copied)} files)")
    return {"tier": tier, "path": str(dest_dir), "files": copied, "timestamp": _timestamp()}


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
    """Check that all expected files exist and are non-empty, valid xlsx files."""
    import openpyxl
    snap_dir = settings.BACKUP_DIR / tier / snapshot
    if not snap_dir.exists():
        return {"valid": False, "reason": "snapshot not found"}

    issues = []
    for filename in DATA_FILES:
        f = snap_dir / filename
        if not f.exists():
            issues.append(f"{filename} missing")
            continue
        try:
            openpyxl.load_workbook(f, read_only=True)
        except Exception as e:
            issues.append(f"{filename} unreadable: {e}")

    return {"valid": len(issues) == 0, "issues": issues}


def restore_backup(tier: str, snapshot: str, actor: str = "admin") -> dict:
    """
    Restores files from a backup snapshot back into the live data directory.
    A safety backup of the CURRENT state is taken first so a restore is reversible.
    """
    validation = validate_backup(tier, snapshot)
    if not validation["valid"]:
        raise ValueError(f"Cannot restore invalid backup: {validation['issues']}")

    # Safety net: snapshot current state before overwriting.
    run_backup("hourly")

    snap_dir = settings.BACKUP_DIR / tier / snapshot
    restored = []
    for filename in DATA_FILES:
        src = snap_dir / filename
        if src.exists():
            dst = settings.DATA_DIR / filename
            shutil.copy2(src, dst)
            restored.append(filename)

    log_engine.log_event(
        "BACKUP_RESTORED",
        description=f"Restored from {tier}/{snapshot}: {restored}",
        actor=actor,
    )
    return {"restored_files": restored, "from": f"{tier}/{snapshot}"}
