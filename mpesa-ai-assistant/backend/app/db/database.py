"""
Database connection setup for Supabase (Postgres).

Uses a simple session-per-call pattern to match the rest of the app's
style (each function in db_engine opens a session, does its work, and
closes it) rather than threading FastAPI's Depends(get_db) through every
route — keeps this migration's blast radius limited to the storage layer.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping avoids "server closed the connection unexpectedly" errors
# after periods of idleness, which Supabase's connection pooler can trigger.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
