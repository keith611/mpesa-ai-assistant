"""
AI Service Layer — PLACEHOLDER ONLY.

This module defines the interface future AI features will use
(financial insights, spending analysis, NLU for WhatsApp, smart
categorization, recommendations). It is intentionally NOT connected to
any AI provider right now. Every function returns a deterministic,
rule-based, or "not yet available" response so the rest of the system
can call these functions today and get real AI behavior later just by
filling in the function bodies — no architecture changes needed.

DO NOT add API calls to OpenAI/Claude/Gemini/etc. here until explicitly
instructed to move to the AI phase.
"""
from typing import Optional


class AIServiceUnavailable(Exception):
    """Raised by placeholder functions to make it explicit AI isn't wired up yet."""
    pass


def generate_financial_insight(user_id: str, transactions: list[dict]) -> str:
    """
    FUTURE: Summarize a user's financial behavior in natural language.
    NOW: Returns a simple rule-based observation.
    """
    if not transactions:
        return "Not enough transaction history yet to generate insights."
    total = sum(t.get("Amount", 0) for t in transactions)
    return f"You had {len(transactions)} transactions totaling KES {total:,.2f} recently."


def analyze_spending_pattern(user_id: str, spending_by_category: dict) -> str:
    """
    FUTURE: Use AI to detect unusual spending patterns / trends.
    NOW: Returns the top spending category as a plain rule-based statement.
    """
    if not spending_by_category:
        return "No spending data available for this period."
    top_category = max(spending_by_category, key=spending_by_category.get)
    return f"Your highest spending category was {top_category} (KES {spending_by_category[top_category]:,.2f})."


def parse_natural_language_query(message_text: str) -> Optional[str]:
    """
    FUTURE: Use an LLM to understand free-form WhatsApp messages and map
    them to an intent/command.
    NOW: Returns None — the WhatsApp bot's rule-based command matcher
    handles all messages instead of this function.
    """
    return None


def suggest_category(sender: str, receiver: str, account_reference: str) -> Optional[str]:
    """
    FUTURE: Use AI to categorize ambiguous transactions the rule engine
    can't confidently classify.
    NOW: Returns None — falls back to rule-based categorization.
    """
    return None


def generate_recommendation(user_id: str, financial_summary: dict) -> str:
    """
    FUTURE: Personalized savings/budgeting recommendations.
    NOW: Static placeholder message.
    """
    return "Personalized recommendations will be available in a future update."
