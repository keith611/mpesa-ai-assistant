"""
Factory for getting the active WhatsApp service implementation.
Everything in the app should call get_whatsapp_service() rather than
importing MockWhatsAppService / CloudAPIWhatsAppService directly.
"""
from app.core.config import get_settings
from app.services.whatsapp.base import WhatsAppServiceBase
from app.services.whatsapp.mock_service import get_mock_service

settings = get_settings()


def get_whatsapp_service() -> WhatsAppServiceBase:
    if settings.WHATSAPP_MODE == "live":
        # Imported lazily so `httpx` and live credentials are only required
        # when someone actually opts into live mode.
        from app.services.whatsapp.cloud_service import CloudAPIWhatsAppService
        return CloudAPIWhatsAppService()
    return get_mock_service()
