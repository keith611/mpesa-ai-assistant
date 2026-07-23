"""
M-Pesa AI Assistant — FastAPI application entrypoint.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.services.scheduler import start_scheduler, stop_scheduler
from app.db_engine import users as user_engine
from app.db_engine import transactions as txn_engine
from app.db_engine import logs as log_engine
from app.db_engine import categorization as cat_engine
from app.db_engine import analytics as analytics_engine

from app.api import auth, users, transactions, reports, admin, whatsapp
from app.api import extras

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure all Postgres tables exist, seed default data, start scheduler.
    user_engine.init()
    txn_engine.init()
    cat_engine.init()
    analytics_engine.init()
    log_engine.init()
    log_engine.log_event("SYSTEM_STARTUP", description=f"{settings.APP_NAME} backend started")
    start_scheduler()
    yield
    # Shutdown
    log_engine.log_event("SYSTEM_SHUTDOWN", description=f"{settings.APP_NAME} backend stopped")
    stop_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for the M-Pesa AI Assistant platform (Postgres/Supabase-backed, WhatsApp-facing).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(extras.router)
app.include_router(users.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(whatsapp.router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV, "whatsapp_mode": settings.WHATSAPP_MODE}
