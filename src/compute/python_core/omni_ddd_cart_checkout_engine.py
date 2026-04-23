import datetime
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniDDDCartCheckoutEngine:
    """
    OmniDDDCartCheckoutEngine
    Batch: 26 (Semester 10)
    Source: g12-4soat/tech-lanches
    
    A zero-mock engine for computing Domain-Driven Design constraints
    applied to cart checkout flows. Validates state constraints,
    computes subtotals, and dynamically applies the highest eligible 
    tiered discount threshold.
    """
    
    def __init__(self, discount_tiers: Dict[float, float]):
        """
        :param discount_tiers: Mapping of spend thresholds to discount multipliers.
                               Example: {100.0: 0.10, 50.0: 0.05} (10% off over 100).
        """
        self.discount_tiers = discount_tiers

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "discount_tiers_count": len(self.discount_tiers),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _validate_cart(self, items: List[Dict[str, Any]]) -> Result[bool, Exception]:
        """
        Enforce strict invariant rules on the cart items wrapper.
        """
        if not isinstance(items, list):
            return Err(TypeError("Items must be a list"))
        if len(items) == 0:
            return Err(ValueError("Cannot checkout an empty cart"))
            
        for idx, item in enumerate(items):
            if "price" not in item or "qty" not in item:
                return Err(KeyError(f"Item at index {idx} missing 'price' or 'qty'"))
                
            if item["qty"] <= 0:
                return Err(ValueError(f"Item at index {idx} has invalid qty: {item['qty']}"))
            
            if item["price"] < 0:
                return Err(ValueError(f"Item at index {idx} has negative price: {item['price']}"))
                
        return Ok(True)

    def compute_subtotal(self, items: List[Dict[str, Any]]) -> Result[float, Exception]:
        """Perform compute subtotal computation.

            Args:
                    items: List[Dict[str
                    Any]]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            val_res = self._validate_cart(items)
            if not val_res.is_ok():
                return Err(val_res.unwrap_err())
                
            subtotal = sum((item["price"] * item["qty"]) for item in items)
            return Ok(round(subtotal, 2))
        except Exception as e:
            return Err(e)

    def compute_discount(self, subtotal: float) -> Result[float, Exception]:
        """
        Find the highest eligible discount tier and compute the absolute discount amount.
        """
        try:
            if subtotal < 0:
                return Err(ValueError("Subtotal cannot be negative"))
                
            applicable_discount = 0.0
            
            # Sort thresholds descending to find the highest bracket
            sorted_tiers = sorted(self.discount_tiers.items(), key=lambda t: t[0], reverse=True)
            
            for threshold, discount_pct in sorted_tiers:
                if subtotal >= threshold:
                    # Apply this tier
                    applicable_discount = subtotal * discount_pct
                    break
                    
            return Ok(round(applicable_discount, 2))
        except Exception as e:
            return Err(e)

    def process_checkout(self, items: List[Dict[str, Any]]) -> Result[Dict[str, Any], Exception]:
        """
        Execute full checkout lifecycle computing the final invariant state transaction tuple.
        """
        try:
            subtotal_res = self.compute_subtotal(items)
            if not subtotal_res.is_ok():
                return Err(subtotal_res.unwrap_err())
                
            subtotal = subtotal_res.unwrap()
            
            discount_res = self.compute_discount(subtotal)
            if not discount_res.is_ok():
                return Err(discount_res.unwrap_err())
                
            discount = discount_res.unwrap()
            final_total = max(0.0, subtotal - discount)
            
            transaction_state = {
                "transaction_id": f"TX-{int(datetime.datetime.utcnow().timestamp())}",
                "item_count": sum(i["qty"] for i in items),
                "subtotal": subtotal,
                "discount_applied": discount,
                "final_total": round(final_total, 2),
                "status": "APPROVED"
            }
            
            return Ok(transaction_state)
            
        except Exception as e:
            return Err(e)
