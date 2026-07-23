"""
Central configuration for the M-Pesa AI Assistant backend.
All values are loaded from environment variables (see .env.example).
Never hardcode secrets here.
"""
import os
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


def _env_list(key: str, default: str = "") -> list[str]:
    raw = os.getenv(key, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings:
    # --- App ---
    APP_NAME: str = os.getenv("APP_NAME", "M-Pesa AI Assistant")
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # --- Security / JWT ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # --- Database (Supabase / Postgres) ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # --- API keys for internal services (Android app, WhatsApp webhook, etc.) ---
    DEVICE_API_KEY: str = os.getenv("DEVICE_API_KEY", "CHANGE_ME_DEVICE_KEY")

    # --- WhatsApp Cloud API ---
    # WHATSAPP_MODE controls which implementation is used:
    #   "mock" (default) -> no credentials needed, messages are captured in-memory/logged, safe for local dev
    #   "live"            -> calls the real Meta Graph API using the credentials below
    WHATSAPP_MODE: str = os.getenv("WHATSAPP_MODE", "mock").lower()
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "CHANGE_ME_WHATSAPP_TOKEN")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v20.0")
    WHATSAPP_APP_SECRET: str = os.getenv("WHATSAPP_APP_SECRET", "")  # used to verify webhook signatures in live mode

    # --- Dev/testing helpers (should be disabled in production) ---
    ENABLE_WHATSAPP_SIMULATOR: bool = os.getenv("ENABLE_WHATSAPP_SIMULATOR", "true").lower() == "true"

    # --- CORS ---
    CORS_ORIGINS: list[str] = _env_list("CORS_ORIGINS", "http://localhost:3000")

    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # --- Local storage paths (CSV snapshot backups only now; the datastore itself is Postgres) ---
    DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
    BACKUP_DIR: Path = BASE_DIR / os.getenv("BACKUP_DIR", "backups")

    # --- Backup retention ---
    HOURLY_BACKUPS_TO_KEEP: int = int(os.getenv("HOURLY_BACKUPS_TO_KEEP", "24"))
    DAILY_BACKUPS_TO_KEEP: int = int(os.getenv("DAILY_BACKUPS_TO_KEEP", "30"))
    WEEKLY_BACKUPS_TO_KEEP: int = int(os.getenv("WEEKLY_BACKUPS_TO_KEEP", "12"))

    def ensure_directories(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        (self.BACKUP_DIR / "hourly").mkdir(parents=True, exist_ok=True)
        (self.BACKUP_DIR / "daily").mkdir(parents=True, exist_ok=True)
        (self.BACKUP_DIR / "weekly").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
