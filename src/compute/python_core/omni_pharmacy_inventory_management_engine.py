"""OmniPharmacyInventoryManagementEngine — Medicine Inventory & Billing.

Inspired by Atul-Anand-Jha/Pharmacy_Management_Software: a C# Windows
Forms application for medical store management with inventory tracking,
expiry date management, billing, and stock alerts.

Algorithmic Primitive:
    Maintain a medicine inventory with batch-level tracking. Compute
    FEFO (First Expired First Out) dispensing order, generate reorder
    alerts when stock falls below safety thresholds, and calculate
    billing totals with configurable tax and discount rates.
"""
from __future__ import annotations
import sys, os
from datetime import datetime
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniPharmacyInventoryManagementEngine:
    """Production-grade pharmacy inventory engine with FEFO dispensing."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniPharmacyInventoryManagementEngine",
            "version": "1.0.0",
            "primitive": "fefo_inventory_dispensing_reorder_billing",
            "monadic_enforcement": True,
            "source_repo": "Atul-Anand-Jha/Pharmacy_Management_Software",
        }

    @staticmethod
    def compute_fefo_order(batches: list[dict], reference_date: str) -> Result:
        """Sort medicine batches by First Expired First Out order.

        Args:
            batches: List of batch dicts, each with:
                - 'batch_id': str
                - 'medicine': str
                - 'qty': int — quantity in stock
                - 'expiry_date': str — ISO date (YYYY-MM-DD)
            reference_date: str — current date for expiry comparison.

        Returns:
            Result[dict, Exception]: dict with 'dispensing_order' (sorted
            list), 'expired_batches', 'near_expiry_batches' (within 30 days).
        """
        if not isinstance(batches, list) or len(batches) == 0:
            return Err(Exception("batches must be a non-empty list"))

        try:
            ref = datetime.strptime(reference_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            return Err(Exception("reference_date must be ISO format YYYY-MM-DD"))

        expired = []
        near_expiry = []
        valid = []

        for b in batches:
            if not isinstance(b, dict) or "expiry_date" not in b:
                return Err(Exception("Each batch must have 'expiry_date'"))
            try:
                exp = datetime.strptime(b["expiry_date"], "%Y-%m-%d")
            except ValueError:
                return Err(Exception(f"Invalid expiry_date: {b['expiry_date']}"))

            days_to_expiry = (exp - ref).days
            enriched = {**b, "days_to_expiry": days_to_expiry}

            if days_to_expiry < 0:
                expired.append(enriched)
            elif days_to_expiry <= 30:
                near_expiry.append(enriched)
                valid.append(enriched)
            else:
                valid.append(enriched)

        # FEFO: sort by expiry date ascending
        dispensing_order = sorted(valid, key=lambda x: x["expiry_date"])

        return Ok({
            "dispensing_order": dispensing_order,
            "expired_batches": expired,
            "near_expiry_batches": near_expiry,
        })

    @staticmethod
    def check_reorder_alerts(
        inventory: list[dict],
        safety_threshold: int = 10,
    ) -> Result:
        """Identify medicines that need reordering.

        Args:
            inventory: List of dicts with 'medicine' (str) and 'qty' (int).
            safety_threshold: Minimum stock level before alert triggers.

        Returns:
            Result[list[dict], Exception]: List of alerts with medicine
            name and current quantity.
        """
        if not isinstance(inventory, list):
            return Err(Exception("inventory must be a list"))
        if safety_threshold < 0:
            return Err(Exception("safety_threshold must be non-negative"))

        alerts = []
        for item in inventory:
            if not isinstance(item, dict):
                return Err(Exception("Each inventory item must be a dict"))
            qty = item.get("qty", 0)
            if qty <= safety_threshold:
                alerts.append({
                    "medicine": item.get("medicine", "unknown"),
                    "current_qty": qty,
                    "deficit": safety_threshold - qty,
                })

        return Ok(alerts)

    @staticmethod
    def compute_bill(
        line_items: list[dict],
        tax_rate: float = 0.0,
        discount_rate: float = 0.0,
    ) -> Result:
        """Compute a pharmacy bill with tax and discount.

        Args:
            line_items: List of dicts with 'medicine' (str), 'qty' (int),
                        'unit_price' (float).
            tax_rate: Tax rate as decimal (0.18 = 18%).
            discount_rate: Discount rate as decimal (0.10 = 10%).

        Returns:
            Result[dict, Exception]: dict with 'subtotal', 'discount_amount',
            'tax_amount', 'grand_total', 'item_count'.
        """
        if not isinstance(line_items, list) or len(line_items) == 0:
            return Err(Exception("line_items must be a non-empty list"))
        if not (0.0 <= tax_rate <= 1.0):
            return Err(Exception("tax_rate must be between 0.0 and 1.0"))
        if not (0.0 <= discount_rate <= 1.0):
            return Err(Exception("discount_rate must be between 0.0 and 1.0"))

        subtotal = 0.0
        for item in line_items:
            qty = item.get("qty", 0)
            price = item.get("unit_price", 0.0)
            if qty <= 0 or price <= 0:
                return Err(Exception(f"Invalid qty or unit_price for '{item.get('medicine')}'"))
            subtotal += qty * price

        discount_amount = round(subtotal * discount_rate, 2)
        taxable = subtotal - discount_amount
        tax_amount = round(taxable * tax_rate, 2)
        grand_total = round(taxable + tax_amount, 2)

        return Ok({
            "subtotal": round(subtotal, 2),
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "grand_total": grand_total,
            "item_count": len(line_items),
        })
