"""
Abstract interface both the mock and live WhatsApp services implement.
Everything else in the system (the bot, the webhook routes) talks to this
interface only — swapping WHATSAPP_MODE=mock to WHATSAPP_MODE=live requires
no other code changes.
"""
from abc import ABC, abstractmethod
from typing import Optional


class WhatsAppServiceBase(ABC):

    @abstractmethod
    def send_text_message(self, to: str, body: str) -> dict:
        """Send a plain text message. Returns a dict describing the send result."""
        raise NotImplementedError

    @abstractmethod
    def send_document(self, to: str, file_bytes: bytes, filename: str, caption: Optional[str] = None) -> dict:
        """Send a document/file (e.g. an exported report). Returns a dict describing the send result."""
        raise NotImplementedError
