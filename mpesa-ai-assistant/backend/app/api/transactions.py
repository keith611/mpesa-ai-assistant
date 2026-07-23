"""
Transaction endpoints:
- POST /transactions/ingest is used by the Android SMS Reader app (device API key auth)
- The rest are used by the admin dashboard / authenticated users (JWT auth)
"""
import io
from fastapi import APIRouter, HTTPException, Depends, Header, status
from fastapi.responses import StreamingResponse

from app.models.schemas import TransactionCreateRequest
from app.core.deps import get_current_claims, require_min_role
from app.core.config import get_settings
from app.db_engine import transactions as txn_engine

router = APIRouter(prefix="/transactions", tags=["Transactions"])
settings = get_settings()


def verify_device_key(x_device_api_key: str = Header(...)):
    if x_device_api_key != settings.DEVICE_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device API key")
    return True


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_transaction(payload: TransactionCreateRequest, _: bool = Depends(verify_device_key)):
    """Called by the Android SMS Reader app when a new M-Pesa SMS is parsed."""
    try:
        return txn_engine.add_transaction(
            user_id=payload.user_id,
            transaction_code=payload.transaction_code,
            amount=payload.amount,
            transaction_type=payload.transaction_type,
            sender=payload.sender,
            receiver=payload.receiver,
            paybill_number=payload.paybill_number,
            till_number=payload.till_number,
            account_reference=payload.account_reference,
            date=payload.date,
            time=payload.time,
            balance=payload.balance,
            source="SMS",
        )
    except txn_engine.DuplicateTransactionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{transaction_id}")
def get_transaction(transaction_id: str, claims: dict = Depends(get_current_claims)):
    txn = txn_engine.get_transaction(transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if claims.get("role") == "USER" and txn.get("User ID") != claims.get("sub"):
        raise HTTPException(status_code=403, detail="Not authorized to view this transaction")
    return txn


@router.get("")
def search_transactions(user_id: str = None, keyword: str = None, category: str = None,
                         transaction_type: str = None, date_from: str = None, date_to: str = None,
                         min_amount: float = None, max_amount: float = None,
                         page: int = 1, page_size: int = 50,
                         claims: dict = Depends(get_current_claims)):
    # Regular users can only search their own transactions.
    if claims.get("role") == "USER":
        user_id = claims.get("sub")
    return txn_engine.search_transactions(
        user_id=user_id, keyword=keyword, category=category, transaction_type=transaction_type,
        date_from=date_from, date_to=date_to, min_amount=min_amount, max_amount=max_amount,
        page=page, page_size=page_size,
    )


@router.get("/export/csv", dependencies=[Depends(require_min_role("SUPPORT"))])
def export_transactions_csv(user_id: str = None, date_from: str = None, date_to: str = None):
    df = txn_engine.export_transactions(user_id=user_id, date_from=date_from, date_to=date_to)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"},
    )
