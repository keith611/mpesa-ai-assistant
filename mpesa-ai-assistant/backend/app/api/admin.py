"""
Admin-only endpoints: backup management and category rule editing.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import require_min_role, get_current_claims
from app.db_engine import backup as backup_engine
from app.db_engine import categorization as cat_engine
from app.models.schemas import CategoryRuleRequest

router = APIRouter(prefix="/admin", tags=["Admin"])


# ---------- Backups ----------

@router.get("/backups", dependencies=[Depends(require_min_role("ADMIN"))])
def list_backups(tier: str = None):
    return backup_engine.list_backups(tier=tier)


@router.post("/backups/run/{tier}", dependencies=[Depends(require_min_role("ADMIN"))])
def run_backup(tier: str):
    try:
        return backup_engine.run_backup(tier)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/backups/validate", dependencies=[Depends(require_min_role("ADMIN"))])
def validate_backup(tier: str, snapshot: str):
    return backup_engine.validate_backup(tier, snapshot)


@router.post("/backups/restore", dependencies=[Depends(require_min_role("SUPER_ADMIN"))])
def restore_backup(tier: str, snapshot: str, claims: dict = Depends(get_current_claims)):
    try:
        return backup_engine.restore_backup(tier, snapshot, actor=claims["sub"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Category rules ----------

@router.get("/category-rules", dependencies=[Depends(require_min_role("ADMIN"))])
def get_category_rules():
    return cat_engine.get_rules(active_only=False)


@router.post("/category-rules", dependencies=[Depends(require_min_role("ADMIN"))])
def add_category_rule(payload: CategoryRuleRequest, claims: dict = Depends(get_current_claims)):
    try:
        rule_id = cat_engine.add_rule(payload.keyword, payload.category, payload.priority, actor=claims["sub"])
        return {"rule_id": rule_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/category-rules/{rule_id}", dependencies=[Depends(require_min_role("ADMIN"))])
def update_category_rule(rule_id: str, payload: dict, claims: dict = Depends(get_current_claims)):
    try:
        cat_engine.update_rule(rule_id, payload, actor=claims["sub"])
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/category-rules/{rule_id}", dependencies=[Depends(require_min_role("ADMIN"))])
def delete_category_rule(rule_id: str):
    cat_engine.delete_rule(rule_id)
    return {"status": "deleted"}
