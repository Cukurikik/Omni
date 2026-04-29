"""OmniPersonalFinanceBudgetEngine — Budget Tracking & Variance Analysis.

Inspired by samyukthagopalsamy/Personal_Finance_Management_Android_App:
a Java/SQLite Android app for managing personal finances with income/
expense tracking, categorized transactions, and balance computation.

Algorithmic Primitive:
    Process a list of categorized transactions (income/expense), compute
    per-category totals, rolling balance, and budget variance analysis
    (actual vs. planned spending per category).
"""
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniPersonalFinanceBudgetEngine:
    """Production-grade personal finance budget and variance analysis engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniPersonalFinanceBudgetEngine",
            "version": "1.0.0",
            "primitive": "categorized_transaction_budget_variance",
            "monadic_enforcement": True,
            "source_repo": "samyukthagopalsamy/Personal_Finance_Management_Android_App",
        }

    @staticmethod
    def compute_category_totals(transactions: list[dict]) -> Result:
        """Aggregate transaction amounts by category and type.

        Args:
            transactions: List of dicts with:
                - 'type': str — 'income' or 'expense'
                - 'category': str — e.g. 'salary', 'food', 'rent'
                - 'amount': float — positive number

        Returns:
            Result[dict, Exception]: dict with 'income_by_category',
            'expense_by_category', 'total_income', 'total_expense', 'net'.
        """
        if not isinstance(transactions, list):
            return Err(Exception("transactions must be a list"))

        income_cats: dict[str, float] = {}
        expense_cats: dict[str, float] = {}
        total_income = 0.0
        total_expense = 0.0

        for tx in transactions:
            if not isinstance(tx, dict):
                return Err(Exception("Each transaction must be a dict"))
            tx_type = tx.get("type")
            if tx_type not in ("income", "expense"):
                return Err(Exception(f"Invalid transaction type: {tx_type}"))
            amount = tx.get("amount", 0.0)
            if amount < 0:
                return Err(Exception("Transaction amount must be non-negative"))
            category = tx.get("category", "uncategorized")

            if tx_type == "income":
                income_cats[category] = income_cats.get(category, 0.0) + amount
                total_income += amount
            else:
                expense_cats[category] = expense_cats.get(category, 0.0) + amount
                total_expense += amount

        return Ok({
            "income_by_category": income_cats,
            "expense_by_category": expense_cats,
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net": round(total_income - total_expense, 2),
        })

    @staticmethod
    def compute_rolling_balance(
        transactions: list[dict],
        initial_balance: float = 0.0,
    ) -> Result:
        """Compute a running balance from chronologically ordered transactions.

        Args:
            transactions: List of dicts with 'type', 'amount', and
                          optionally 'date' (for labeling).
            initial_balance: Starting balance.

        Returns:
            Result[list[dict], Exception]: List of dicts with 'index',
            'type', 'amount', 'balance_after'.
        """
        if not isinstance(transactions, list):
            return Err(Exception("transactions must be a list"))

        balance = initial_balance
        ledger: list[dict] = []

        for i, tx in enumerate(transactions):
            tx_type = tx.get("type")
            amount = tx.get("amount", 0.0)

            if tx_type == "income":
                balance += amount
            elif tx_type == "expense":
                balance -= amount
            else:
                return Err(Exception(f"Invalid type at index {i}: {tx_type}"))

            ledger.append({
                "index": i,
                "type": tx_type,
                "amount": amount,
                "balance_after": round(balance, 2),
            })

        return Ok(ledger)

    @staticmethod
    def compute_budget_variance(
        budget: dict[str, float],
        actuals: dict[str, float],
    ) -> Result:
        """Compare actual spending against planned budget per category.

        Args:
            budget: dict of category -> planned amount.
            actuals: dict of category -> actual spent amount.

        Returns:
            Result[dict, Exception]: dict with 'variances' (per category),
            'total_budget', 'total_actual', 'total_variance',
            'over_budget_categories'.
        """
        if not isinstance(budget, dict) or not isinstance(actuals, dict):
            return Err(Exception("budget and actuals must be dicts"))

        all_categories = set(budget.keys()) | set(actuals.keys())
        variances: dict[str, dict] = {}
        total_budget = 0.0
        total_actual = 0.0
        over_budget: list[str] = []

        for cat in sorted(all_categories):
            planned = budget.get(cat, 0.0)
            actual = actuals.get(cat, 0.0)
            diff = round(planned - actual, 2)
            total_budget += planned
            total_actual += actual

            variances[cat] = {
                "planned": planned,
                "actual": actual,
                "variance": diff,
                "over_budget": actual > planned,
            }
            if actual > planned:
                over_budget.append(cat)

        return Ok({
            "variances": variances,
            "total_budget": round(total_budget, 2),
            "total_actual": round(total_actual, 2),
            "total_variance": round(total_budget - total_actual, 2),
            "over_budget_categories": over_budget,
        })
