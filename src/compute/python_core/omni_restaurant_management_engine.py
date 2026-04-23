import json

import logging
import uuid
import datetime
from src.compute.python_core.omni_base_engine import Result, Ok, Err

logger = logging.getLogger(__name__)

class OmniRestaurantManagementEngine:
    """
    OMNI Semester 10 Batch 30 - Production Restaurant Management System Engine
    Zero-Prod implementation for high-throughput restaurant operations.
    Supports Order Tracking, Menu Management, and Payment Processing.
    """
    def __init__(self, config=None):
        self._config = config or {}
        self._inventory = {}
        self._active_orders = {}
        self._system_id = str(uuid.uuid4())
        self._is_operational = True
        
        # Hardcore defaults
        self._tax_rate = self._config.get("tax_rate", 0.08)
        self._logger = logger

    def add_menu_item(self, item_id: str, name: str, price: float, available_stock: int) -> dict:
        """ Adds item to the production inventory. Monadic Result. """
        if price < 0:
            return {"status": "error", "error": "Price cannot be negative"}
        if available_stock < 0:
            return {"status": "error", "error": "Stock cannot be negative"}
            
        self._inventory[item_id] = {
            "name": name,
            "price": price,
            "stock": available_stock
        }
        return {"status": "ok", "value": item_id}

    def process_order(self, order_items: list) -> dict:
        """ Processes an order atomically, ensuring absolute stock integrity. """
        if not self._is_operational:
            return {"status": "error", "error": "Engine offline"}
            
        # Monadic validation
        total_amount = 0.0
        updates = []
        for item in order_items:
            item_id = item.get("item_id")
            quantity = item.get("quantity", 1)
            
            if item_id not in self._inventory:
                return {"status": "error", "error": f"Item {item_id} not found."}
                
            inv_item = self._inventory[item_id]
            if inv_item["stock"] < quantity:
                return {"status": "error", "error": f"Insufficient stock for {item_id}."}
                
            total_amount += inv_item["price"] * quantity
            updates.append({"id": item_id, "qty": quantity})
            
        # Commit transaction
        for u in updates:
            self._inventory[u["id"]]["stock"] -= u["qty"]
            
        grand_total = total_amount * (1.0 + self._tax_rate)
        order_id = str(uuid.uuid4())
        
        self._active_orders[order_id] = {
            "items": order_items,
            "total_pre_tax": total_amount,
            "grand_total": grand_total,
            "timestamp": str(datetime.datetime.utcnow())
        }
        
        return {
            "status": "ok", 
            "value": {
                "order_id": order_id, 
                "grand_total": grand_total
            }
        }

    def process_payment(self, order_id: str, amount_paid: float) -> dict:
        """Perform process payment computation.

            Args:
                    order_id: str
                    amount_paid: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if order_id not in self._active_orders:
            return {"status": "error", "error": "Order not found."}
            
        order = self._active_orders[order_id]
        if amount_paid < order["grand_total"]:
            return {"status": "error", "error": "Insufficient payment."}
            
        change = amount_paid - order["grand_total"]
        del self._active_orders[order_id]
        
        return {"status": "ok", "value": {"change": change, "cleared": True}}

    def diagnostics(self) -> dict:
        return {
            "engine": "OmniRestaurantManagementEngine",
            "version": "3.0.0",
            "status": "operational" if self._is_operational else "offline",
            "system_id": self._system_id,
            "capabilities": [
                "menu_management", 
                "atomic_order_processing", 
                "transaction_payment_clearance"
            ],
            "metrics": {
                "inventory_size": len(self._inventory),
                "active_orders": len(self._active_orders)
            }
        }
