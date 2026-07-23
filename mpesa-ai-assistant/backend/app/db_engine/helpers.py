"""
Shared helpers used across the db_engine modules.
"""
import re
from sqlalchemy.orm import Session


def next_id(session: Session, model, id_column_name: str, prefix: str) -> str:
    """
    Generates the next sequential ID like TXN-000042, mirroring the old
    Excel engine's ID scheme. Looks at the highest existing numeric
    suffix for the given prefix and increments it.
    """
    column = getattr(model, id_column_name)
    existing_ids = session.query(column).filter(column.like(f"{prefix}-%")).all()
    max_num = 0
    for (existing_id,) in existing_ids:
        match = re.search(r"(\d+)$", existing_id or "")
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"{prefix}-{max_num + 1:06d}"
