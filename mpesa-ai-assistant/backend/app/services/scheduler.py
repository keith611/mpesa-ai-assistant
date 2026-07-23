"""
Background scheduler that triggers automatic backups.
Started from main.py's startup event using APScheduler.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db_engine import backup as backup_engine
from app.db_engine import analytics as analytics_engine

_scheduler: BackgroundScheduler = None


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(lambda: backup_engine.run_backup("hourly"), CronTrigger(minute=0), id="hourly_backup")
    _scheduler.add_job(lambda: backup_engine.run_backup("daily"), CronTrigger(hour=2, minute=0), id="daily_backup")
    _scheduler.add_job(
        lambda: backup_engine.run_backup("weekly"),
        CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="weekly_backup",
    )
    _scheduler.add_job(
        lambda: analytics_engine.run_full_rollup(actor="scheduler"),
        CronTrigger(hour=1, minute=0),  # daily rollup of current month-to-date figures
        id="analytics_rollup",
    )
    _scheduler.start()
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
