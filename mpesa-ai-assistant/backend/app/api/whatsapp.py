"""
WhatsApp endpoints.

- GET  /whatsapp/webhook           -> Meta's webhook verification handshake (used in live mode)
- POST /whatsapp/webhook           -> receives real inbound messages from Meta (live mode)
- POST /whatsapp/simulate          -> send a fake inbound message locally, no WhatsApp needed (mock/dev mode)
- GET  /whatsapp/outbox            -> view messages the mock service has "sent" (dev/testing only)
- DELETE /whatsapp/outbox          -> clear the mock outbox
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.deps import require_min_role
from app.services.whatsapp_bot import handle_incoming_message
from app.services.whatsapp.factory import get_whatsapp_service
from app.services.whatsapp.mock_service import get_mock_service, MockWhatsAppService

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])
settings = get_settings()


class SimulateMessageRequest(BaseModel):
    whatsapp_number: str
    message_text: str


# ---------- Webhook verification (GET) — required by Meta before it will send events ----------

@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge) if hub_challenge and hub_challenge.isdigit() else hub_challenge
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Webhook verification failed")


# ---------- Inbound message webhook (POST) — real Meta payloads in live mode ----------

@router.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    responses = []

    try:
        entries = payload.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    from_number = msg.get("from")
                    text = msg.get("text", {}).get("body", "")
                    if not from_number or not text:
                        continue
                    result = handle_incoming_message(from_number, text)
                    service = get_whatsapp_service()
                    service.send_text_message(from_number, result["reply"])
                    if result["attachment"]:
                        filename, file_bytes, caption = result["attachment"]
                        service.send_document(from_number, file_bytes, filename, caption)
                    responses.append({"from": from_number, "reply": result["reply"]})
    except Exception:
        # Never let a malformed webhook payload crash the endpoint — Meta will retry on non-200.
        pass

    return {"status": "received", "processed": len(responses)}


# ---------- Local simulator — no WhatsApp credentials required ----------

@router.post("/simulate")
def simulate_incoming_message(payload: SimulateMessageRequest):
    """
    Simulates an inbound WhatsApp message without needing real WhatsApp
    credentials or the Cloud API. Runs the same bot logic the real webhook
    would, and "sends" the reply via whichever service is configured
    (mock by default). Check GET /whatsapp/outbox to see the bot's reply.
    """
    if not settings.ENABLE_WHATSAPP_SIMULATOR:
        raise HTTPException(status_code=403, detail="Simulator is disabled (ENABLE_WHATSAPP_SIMULATOR=false)")

    result = handle_incoming_message(payload.whatsapp_number, payload.message_text)
    service = get_whatsapp_service()
    send_result = service.send_text_message(payload.whatsapp_number, result["reply"])

    attachment_result = None
    if result["attachment"]:
        filename, file_bytes, caption = result["attachment"]
        attachment_result = service.send_document(payload.whatsapp_number, file_bytes, filename, caption)

    return {
        "inbound": {"from": payload.whatsapp_number, "text": payload.message_text},
        "reply": result["reply"],
        "send_result": send_result,
        "attachment_result": attachment_result,
    }


# ---------- Outbox viewer (mock mode only, for local testing) ----------

@router.get("/outbox")
def get_outbox(limit: int = 50):
    if settings.WHATSAPP_MODE != "mock":
        raise HTTPException(status_code=400, detail="Outbox is only available in mock mode")
    service = get_mock_service()
    return {"mode": settings.WHATSAPP_MODE, "messages": service.get_outbox(limit=limit)}


@router.delete("/outbox", dependencies=[Depends(require_min_role("ADMIN"))])
def clear_outbox():
    if settings.WHATSAPP_MODE != "mock":
        raise HTTPException(status_code=400, detail="Outbox is only available in mock mode")
    service = get_mock_service()
    service.clear_outbox()
    return {"status": "cleared"}
