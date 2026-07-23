"""
Live WhatsApp Cloud API service — used when WHATSAPP_MODE=live.

This calls the real Meta Graph API. It does nothing until you set
WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID in your environment.
Until then, keep WHATSAPP_MODE=mock and use MockWhatsAppService instead.

Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
"""
import base64
from typing import Optional

import httpx

from app.core.config import get_settings
from app.services.whatsapp.base import WhatsAppServiceBase
from app.db_engine import logs as log_engine

settings = get_settings()


class WhatsAppNotConfiguredError(Exception):
    """Raised when live mode is selected but credentials are missing."""
    pass


class CloudAPIWhatsAppService(WhatsAppServiceBase):
    def __init__(self):
        if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
            raise WhatsAppNotConfiguredError(
                "WHATSAPP_MODE=live but WHATSAPP_ACCESS_TOKEN / WHATSAPP_PHONE_NUMBER_ID "
                "are not set. Add real credentials to .env, or switch WHATSAPP_MODE=mock."
            )
        self.base_url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    def send_text_message(self, to: str, body: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }
        return self._post("/messages", payload)

    def send_document(self, to: str, file_bytes: bytes, filename: str, caption: Optional[str] = None) -> dict:
        # Real implementation requires a two-step upload (media upload, then send-by-id).
        media_id = self._upload_media(file_bytes, filename)
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {"id": media_id, "filename": filename, "caption": caption or ""},
        }
        return self._post("/messages", payload)

    def _upload_media(self, file_bytes: bytes, filename: str) -> str:
        with httpx.Client(timeout=30) as client:
            files = {"file": (filename, file_bytes, "application/octet-stream")}
            data = {"messaging_product": "whatsapp"}
            headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"}
            resp = client.post(f"{self.base_url}/media", headers=headers, data=data, files=files)
            resp.raise_for_status()
            return resp.json()["id"]

    def _post(self, path: str, payload: dict) -> dict:
        with httpx.Client(timeout=15) as client:
            resp = client.post(f"{self.base_url}{path}", headers=self.headers, json=payload)
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                log_engine.log_event(
                    "WHATSAPP_SEND_FAILED", status="ERROR",
                    description=f"to={payload.get('to')} error={e}", actor="whatsapp_live",
                )
                raise
            log_engine.log_event(
                "WHATSAPP_MESSAGE_SENT",
                description=f"(live) to={payload.get('to')} type={payload.get('type')}",
                actor="whatsapp_live",
            )
            return resp.json()
