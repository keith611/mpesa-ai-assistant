"""
Rule-based WhatsApp command bot.

Handles the exact command set from the spec, matched case-insensitively
against normalized inbound text. No AI — pure rule-based intent matching
via keyword/phrase lookup. `app/services/ai_service.parse_natural_language_query`
is called first as a hook for future NLU, but currently always returns
None, so control always falls through to this rule engine.
"""
import io
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.db_engine import users as user_engine
from app.db_engine import transactions as txn_engine
from app.services import ai_service
from app.services import password_reset


def _today():
    return datetime.now(timezone.utc).date()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _fmt_money(amount) -> str:
    try:
        return f"KES {float(amount):,.2f}"
    except (TypeError, ValueError):
        return "KES 0.00"


def _period_bounds(period: str) -> tuple[str, str]:
    today = _today()
    if period == "today":
        return today.isoformat(), today.isoformat()
    if period == "week":
        start = today - timedelta(days=today.weekday())
        return start.isoformat(), today.isoformat()
    if period == "month":
        return today.replace(day=1).isoformat(), today.isoformat()
    return today.replace(day=1).isoformat(), today.isoformat()


# ---------- Individual command handlers ----------
# Each handler takes (user: dict) and returns (reply_text, attachment or None)
# attachment, if present, is a tuple (filename, bytes, caption)

def _handle_balance(user: dict):
    balance = txn_engine.latest_balance(user["User ID"])
    if balance is None:
        return "No balance information found yet. It will appear once your first M-Pesa transaction is recorded.", None
    return f"💰 Your latest M-Pesa balance is {_fmt_money(balance)}.", None


def _handle_spending(user: dict, period: str, label: str):
    date_from, date_to = _period_bounds(period)
    summary = txn_engine.spending_summary(user["User ID"], date_from, date_to)
    if summary["transaction_count"] == 0:
        return f"No transactions found for {label}.", None
    lines = [f"📊 {label} spending: {_fmt_money(summary['total_spent'])}"]
    if summary["by_category"]:
        lines.append("\nBy category:")
        for cat, amt in sorted(summary["by_category"].items(), key=lambda x: -x[1]):
            lines.append(f"  • {cat}: {_fmt_money(amt)}")
    return "\n".join(lines), None


def _handle_income_this_month(user: dict):
    date_from, date_to = _period_bounds("month")
    summary = txn_engine.spending_summary(user["User ID"], date_from, date_to)
    return f"💵 Income this month: {_fmt_money(summary['total_income'])}", None


def _handle_last_transactions(user: dict, count: int = 10):
    txns = txn_engine.list_transactions_for_user(user["User ID"], limit=count)
    if not txns:
        return "No transactions found yet.", None
    lines = [f"🧾 Your last {len(txns)} transactions:"]
    for t in txns:
        lines.append(f"  • {t.get('Date', '')} — {t.get('Transaction Type', '')} {_fmt_money(t.get('Amount'))} ({t.get('Category', 'Other')})")
    return "\n".join(lines), None


def _handle_category_expenses(user: dict, category: str):
    date_from, date_to = _period_bounds("month")
    summary = txn_engine.spending_summary(user["User ID"], date_from, date_to)
    amount = summary["by_category"].get(category, 0)
    return f"⛽ {category} expenses this month: {_fmt_money(amount)}" if category == "Fuel" \
        else f"🍽 {category} expenses this month: {_fmt_money(amount)}", None


def _handle_export_report(user: dict):
    df = txn_engine.export_transactions(user_id=user["User ID"])
    if df.empty:
        return "No transactions to export yet.", None
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    file_bytes = buf.getvalue().encode("utf-8")
    filename = f"transactions_{user['User ID']}_{_today().isoformat()}.csv"
    return "📄 Here is your transaction report.", (filename, file_bytes, "Your M-Pesa transaction export")


def _handle_monthly_summary(user: dict):
    date_from, date_to = _period_bounds("month")
    summary = txn_engine.spending_summary(user["User ID"], date_from, date_to)
    insight = ai_service.generate_financial_insight(user["User ID"], txn_engine.list_transactions_for_user(user["User ID"], limit=100))
    lines = [
        "📅 Monthly Summary",
        f"Income: {_fmt_money(summary['total_income'])}",
        f"Expenses: {_fmt_money(summary['total_spent'])}",
        f"Net: {_fmt_money(summary['total_income'] - summary['total_spent'])}",
        f"Transactions: {summary['transaction_count']}",
        "",
        insight,
    ]
    return "\n".join(lines), None


def _handle_largest_transaction(user: dict):
    txn = txn_engine.largest_transaction(user["User ID"])
    if not txn:
        return "No transactions found yet.", None
    return (f"🏆 Largest transaction: {_fmt_money(txn.get('Amount'))} "
            f"({txn.get('Transaction Type', '')}) on {txn.get('Date', '')}"), None


def _handle_transactions_today(user: dict):
    today = _today().isoformat()
    result = txn_engine.search_transactions(user_id=user["User ID"], date_from=today, date_to=today, page_size=50)
    if result["total"] == 0:
        return "No transactions recorded today.", None
    lines = [f"📆 Today's transactions ({result['total']}):"]
    for t in result["transactions"]:
        lines.append(f"  • {t.get('Time', '')} — {t.get('Transaction Type', '')} {_fmt_money(t.get('Amount'))}")
    return "\n".join(lines), None


def _handle_reset_password(user: dict):
    result = password_reset.request_reset_code(user["Phone Number"])
    code = result.get("code")
    if not code:
        return "Couldn't generate a reset code right now. Please try again shortly.", None
    return (
        f"🔐 Your password reset code is {code}. It expires in {result['expires_in_minutes']} minutes.\n"
        f"Enter this code in the app's 'Forgot password' screen along with your new password."
    ), None


def _handle_help(user: Optional[dict] = None):
    return (
        "👋 Available commands:\n"
        "• Balance\n• Today's spending\n• This week's spending\n• This month's spending\n"
        "• Income this month\n• Last 10 transactions\n• Fuel expenses\n• Food expenses\n"
        "• Export report\n• Monthly summary\n• Largest transaction\n• Transactions today"
    ), None


# ---------- Command routing table ----------
# (list of trigger phrases, handler) — first match wins, checked in order.
_COMMAND_TABLE = [
    (["balance"], lambda u: _handle_balance(u)),
    (["today's spending", "todays spending", "spending today"], lambda u: _handle_spending(u, "today", "Today's")),
    (["this week's spending", "weekly spending", "week spending"], lambda u: _handle_spending(u, "week", "This week's")),
    (["this month's spending", "monthly spending", "month spending"], lambda u: _handle_spending(u, "month", "This month's")),
    (["income this month", "monthly income"], lambda u: _handle_income_this_month(u)),
    (["last 10 transactions", "last transactions", "recent transactions"], lambda u: _handle_last_transactions(u, 10)),
    (["fuel expenses", "fuel spending"], lambda u: _handle_category_expenses(u, "Fuel")),
    (["food expenses", "food spending"], lambda u: _handle_category_expenses(u, "Food")),
    (["export report", "export transactions", "download report"], lambda u: _handle_export_report(u)),
    (["monthly summary", "month summary"], lambda u: _handle_monthly_summary(u)),
    (["largest transaction", "biggest transaction"], lambda u: _handle_largest_transaction(u)),
    (["transactions today", "today's transactions"], lambda u: _handle_transactions_today(u)),
    (["reset password", "forgot password", "change password"], lambda u: _handle_reset_password(u)),
    (["help", "menu", "commands", "hi", "hello"], lambda u: _handle_help(u)),
]


def route_command(text: str, user: dict):
    """Matches normalized text against the command table. Returns (reply, attachment)."""
    normalized = _normalize(text)

    # Hook for future AI/NLU — currently always returns None (see ai_service.py).
    ai_intent = ai_service.parse_natural_language_query(text)
    if ai_intent:
        normalized = ai_intent

    for phrases, handler in _COMMAND_TABLE:
        if any(phrase in normalized for phrase in phrases):
            return handler(user)

    return (
        "🤔 I didn't understand that. Type 'help' to see the list of commands I understand.",
        None,
    )


def handle_incoming_message(whatsapp_number: str, message_text: str) -> dict:
    """
    Main entry point called by the webhook / simulator.
    Returns {"reply": str, "attachment": (filename, bytes, caption) | None}
    """
    user = user_engine.get_user_by_whatsapp(whatsapp_number)

    if not user:
        return {
            "reply": (
                "👋 This WhatsApp number isn't linked to an M-Pesa AI Assistant account yet. "
                "Please register first (ask your admin, or use the registration flow) with this "
                "number as your WhatsApp number."
            ),
            "attachment": None,
        }

    if user.get("Status") != "ACTIVE":
        return {"reply": f"Your account is currently {user.get('Status', 'inactive')}. Please contact support.", "attachment": None}

    user_engine.touch_last_activity(user["User ID"])
    reply, attachment = route_command(message_text, user)
    return {"reply": reply, "attachment": attachment}
