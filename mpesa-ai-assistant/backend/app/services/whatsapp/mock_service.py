"""
Mock WhatsApp service — used when WHATSAPP_MODE=mock (the default).

Requires NO real WhatsApp Cloud API credentials. Instead of calling Meta's
Graph API, it:
  - Stores every "sent" message in an in-memory outbox (viewable via
    GET /api/v1/whatsapp/outbox for local testing)
  - Optionally prints messages to the console
  - Logs every send to SystemLogs.xlsx like a real send would

This lets you fully exercise the WhatsApp command bot end-to-end — sending
inbound messages via the simulator endpoint and reading the bot's replies
from the outbox — without ever touching Meta's infrastructure.
"""
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Optional

from app.services.whatsapp.base import WhatsAppServiceBase
from app.db_engine import logs as log_engine

_OUTBOX_MAX_SIZE = 500


class MockWhatsAppService(WhatsAppServiceBase):
    def __init__(self, log_to_console: bool = True):
        self.log_to_console = log_to_console
        self._outbox: deque[dict] = deque(maxlen=_OUTBOX_MAX_SIZE)
        self._lock = threading.Lock()

    def send_text_message(self, to: str, body: str) -> dict:
        entry = {
            "type": "text",
            "to": to,
            "body": body,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "mock_sent",
        }
        self._store(entry)
        return {"status": "mock_sent", "to": to, "message_type": "text"}

    def send_document(self, to: str, file_bytes: bytes, filename: str, caption: Optional[str] = None) -> dict:
        entry = {
            "type": "document",
            "to": to,
            "filename": filename,
            "caption": caption or "",
            "size_bytes": len(file_bytes),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "mock_sent",
        }
        self._store(entry)
        return {"status": "mock_sent", "to": to, "message_type": "document", "filename": filename}

    def _store(self, entry: dict):
        with self._lock:
            self._outbox.append(entry)
        if self.log_to_console:
            preview = entry.get("body", f"[document: {entry.get('filename')}]")
            print(f"[MockWhatsApp] -> {entry['to']}: {preview}")
        log_engine.log_event(
            "WHATSAPP_MESSAGE_SENT",
            description=f"(mock) to={entry['to']} type={entry['type']}",
            actor="whatsapp_mock",
        )

    def get_outbox(self, limit: int = 50) -> list[dict]:
        with self._lock:
            return list(self._outbox)[-limit:][::-1]

    def clear_outbox(self):
        with self._lock:
            self._outbox.clear()


# Module-level singleton so the outbox persists across requests within one process.
_mock_instance: Optional[MockWhatsAppService] = None


def get_mock_service() -> MockWhatsAppService:
    global _mock_instance
    if _mock_instance is None:
        _mock_instance = MockWhatsAppService()
    return _mock_instance
