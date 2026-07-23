"""
Rule-based transaction categorization (NO AI). Rules now live in the
category_rules Postgres table instead of an Excel sheet, editable the
same way by admins via the API.
"""
from datetime import datetime, timezone

from app.db.database import get_session, Base, engine
from app.db.models import CategoryRule
from app.db_engine.helpers import next_id

VALID_CATEGORIES = [
    "Food", "Transport", "Fuel", "Rent", "Utilities", "Business",
    "Shopping", "Entertainment", "Education", "Healthcare", "Other",
]

DEFAULT_RULES = [
    ("NAIVAS", "Shopping", 10), ("CARREFOUR", "Shopping", 10), ("QUICKMART", "Shopping", 10),
    ("SUPERMARKET", "Shopping", 10),
    ("SHELL", "Fuel", 10), ("TOTAL", "Fuel", 10), ("RUBIS", "Fuel", 10), ("PETROL", "Fuel", 10), ("OILIBYA", "Fuel", 10),
    ("UBER", "Transport", 10), ("BOLT", "Transport", 10), ("MATATU", "Transport", 10), ("TAXI", "Transport", 10),
    ("KPLC", "Utilities", 10), ("NAIROBI WATER", "Utilities", 10), ("DSTV", "Utilities", 10), ("ZUKU", "Utilities", 10),
    ("SAFARICOM", "Utilities", 5),
    ("LANDLORD", "Rent", 10), ("RENT", "Rent", 10),
    ("HOSPITAL", "Healthcare", 10), ("CLINIC", "Healthcare", 10), ("PHARMACY", "Healthcare", 10), ("CHEMIST", "Healthcare", 10),
    ("SCHOOL", "Education", 10), ("UNIVERSITY", "Education", 10), ("COLLEGE", "Education", 10), ("FEES", "Education", 8),
    ("RESTAURANT", "Food", 10), ("HOTEL", "Food", 5), ("EATERY", "Food", 10), ("BUTCHERY", "Food", 10), ("CAFE", "Food", 10),
    ("NETFLIX", "Entertainment", 10), ("SHOWMAX", "Entertainment", 10), ("CINEMA", "Entertainment", 10),
]


def init():
    Base.metadata.create_all(bind=engine, tables=[CategoryRule.__table__])
    with get_session() as session:
        count = session.query(CategoryRule).count()
        if count == 0:
            now = datetime.now(timezone.utc).isoformat()
            for i, (keyword, category, priority) in enumerate(DEFAULT_RULES, start=1):
                session.add(CategoryRule(
                    rule_id=f"RULE-{i:04d}",
                    keyword=keyword,
                    category=category,
                    priority=priority,
                    active=True,
                    updated_by="system",
                    updated_at=now,
                ))


def _to_display_dict(r: CategoryRule) -> dict:
    return {
        "Rule ID": r.rule_id,
        "Keyword": r.keyword,
        "Category": r.category,
        "Priority": r.priority,
        "Active": r.active,
        "Updated By": r.updated_by,
        "Updated At": r.updated_at,
    }


def get_rules(active_only: bool = True):
    init()
    with get_session() as session:
        query = session.query(CategoryRule)
        if active_only:
            query = query.filter(CategoryRule.active == True)  # noqa: E712
        rules = query.order_by(CategoryRule.priority.desc()).all()
        return [_to_display_dict(r) for r in rules]


def add_rule(keyword: str, category: str, priority: int = 5, actor: str = "admin"):
    init()
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}")
    with get_session() as session:
        rule_id = next_id(session, CategoryRule, "rule_id", "RULE")
        rule = CategoryRule(
            rule_id=rule_id,
            keyword=keyword.upper(),
            category=category,
            priority=priority,
            active=True,
            updated_by=actor,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        session.add(rule)
        session.flush()
        return rule_id


def update_rule(rule_id: str, updates: dict, actor: str = "admin"):
    init()
    field_map = {"Keyword": "keyword", "Category": "category", "Priority": "priority", "Active": "active"}
    with get_session() as session:
        rule = session.query(CategoryRule).filter(CategoryRule.rule_id == rule_id).first()
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")
        for key in ("Keyword", "Category", "Priority", "Active"):
            if key in updates:
                setattr(rule, field_map[key], updates[key])
        rule.updated_by = actor
        rule.updated_at = datetime.now(timezone.utc).isoformat()


def delete_rule(rule_id: str):
    init()
    with get_session() as session:
        rule = session.query(CategoryRule).filter(CategoryRule.rule_id == rule_id).first()
        if rule:
            session.delete(rule)


def categorize(transaction_type: str, sender: str = "", receiver: str = "",
                account_reference: str = "") -> str:
    """
    Rule-based categorization. Checks keywords against sender/receiver/
    account reference text. Falls back to "Other".
    """
    haystack = " ".join([str(sender or ""), str(receiver or ""), str(account_reference or "")]).upper()

    for rule in get_rules(active_only=True):
        if rule["Keyword"] in haystack:
            return rule["Category"]

    return "Other"
