"""
Rule-based transaction categorization (NO AI).

Rules are stored in Analytics.xlsx -> CategoryRules sheet so admins can
edit them without touching code. Default rules are seeded on first run.
"""
from datetime import datetime, timezone

from app.core.config import get_settings
from app.excel_engine.base import ensure_multi_sheet_file, read_sheet, atomic_write_sheet, next_id

settings = get_settings()
ANALYTICS_SHEETS = ["MonthlyReports", "SpendingReports", "IncomeReports", "UserStatistics"]
RULES_SHEET = "CategoryRules"

VALID_CATEGORIES = [
    "Food", "Transport", "Fuel", "Rent", "Utilities", "Business",
    "Shopping", "Entertainment", "Education", "Healthcare", "Other",
]

DEFAULT_RULES = [
    # (keyword, category, priority) — checked against Sender/Receiver/Account Reference, case-insensitive
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
    ensure_multi_sheet_file(settings.ANALYTICS_FILE, ANALYTICS_SHEETS + [RULES_SHEET])
    df = read_sheet(settings.ANALYTICS_FILE, RULES_SHEET)
    if df.empty:
        rows = []
        for i, (keyword, category, priority) in enumerate(DEFAULT_RULES, start=1):
            rows.append({
                "Rule ID": f"RULE-{i:04d}",
                "Keyword": keyword,
                "Category": category,
                "Priority": priority,
                "Active": True,
                "Updated By": "system",
                "Updated At": datetime.now(timezone.utc).isoformat(),
            })
        import pandas as pd
        atomic_write_sheet(settings.ANALYTICS_FILE, RULES_SHEET, pd.DataFrame(rows))


def get_rules(active_only: bool = True):
    init()
    df = read_sheet(settings.ANALYTICS_FILE, RULES_SHEET)
    if active_only and not df.empty:
        df = df[df["Active"] == True]  # noqa: E712
    return df.sort_values("Priority", ascending=False).to_dict(orient="records") if not df.empty else []


def add_rule(keyword: str, category: str, priority: int = 5, actor: str = "admin"):
    init()
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}")
    df = read_sheet(settings.ANALYTICS_FILE, RULES_SHEET)
    rule_id = next_id(df, "Rule ID", "RULE")
    import pandas as pd
    new_row = pd.DataFrame([{
        "Rule ID": rule_id, "Keyword": keyword.upper(), "Category": category,
        "Priority": priority, "Active": True, "Updated By": actor,
        "Updated At": datetime.now(timezone.utc).isoformat(),
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    atomic_write_sheet(settings.ANALYTICS_FILE, RULES_SHEET, df)
    return rule_id


def update_rule(rule_id: str, updates: dict, actor: str = "admin"):
    init()
    df = read_sheet(settings.ANALYTICS_FILE, RULES_SHEET)
    idx = df.index[df["Rule ID"] == rule_id]
    if idx.empty:
        raise ValueError(f"Rule {rule_id} not found")
    for key in ("Keyword", "Category", "Priority", "Active"):
        if key in updates:
            df.loc[idx, key] = updates[key]
    df.loc[idx, "Updated By"] = actor
    df.loc[idx, "Updated At"] = datetime.now(timezone.utc).isoformat()
    atomic_write_sheet(settings.ANALYTICS_FILE, RULES_SHEET, df)


def delete_rule(rule_id: str):
    init()
    df = read_sheet(settings.ANALYTICS_FILE, RULES_SHEET)
    df = df[df["Rule ID"] != rule_id]
    atomic_write_sheet(settings.ANALYTICS_FILE, RULES_SHEET, df)


def categorize(transaction_type: str, sender: str = "", receiver: str = "",
                account_reference: str = "") -> str:
    """
    Rule-based categorization. Checks keywords against sender/receiver/
    account reference text. Falls back to transaction-type heuristics,
    then "Other".
    """
    haystack = " ".join([str(sender or ""), str(receiver or ""), str(account_reference or "")]).upper()

    for rule in get_rules(active_only=True):
        if rule["Keyword"] in haystack:
            return rule["Category"]

    txn_type = (transaction_type or "").upper()
    if "SEND" in txn_type or "PAYBILL" in txn_type or "TILL" in txn_type or "BUY GOODS" in txn_type:
        return "Other"
    if "RECEIVE" in txn_type or "DEPOSIT" in txn_type:
        return "Other"
    if "WITHDRAW" in txn_type:
        return "Other"

    return "Other"
