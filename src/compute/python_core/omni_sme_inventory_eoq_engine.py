import math
import datetime
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniSMEInventoryEOQEngine:
    """
    OmniSMEInventoryEOQEngine
    Batch: 26 (Semester 10)
    Source: hossainchisty/SME-Inventory-Management
    
    A zero-mock engine for continuous inventory replenishment metrics.
    Computes the precise Economic Order Quantity (EOQ) and Reorder Point (ROP) 
    base on annual demand variance, structural costs, and dynamic lead times.
    """
    
    def __init__(self, holding_cost_pct: float, operating_days_per_year: int = 365):
        """
        :param holding_cost_pct: Annual holding cost represented as a percentage of unit cost (e.g. 0.20 for 20%)
        :param operating_days_per_year: Number of days the SME operates annually, to compute daily demand.
        """
        self.holding_cost_pct = holding_cost_pct
        self.operating_days_per_year = operating_days_per_year

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "holding_cost_pct": self.holding_cost_pct,
            "operating_days_per_year": self.operating_days_per_year,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def compute_eoq(self, annual_demand: int, setup_ordering_cost: float, unit_cost: float) -> Result[int, Exception]:
        """
        Calculates the Economic Order Quantity.
        Formula: EOQ = sqrt((2 * D * S) / H)
        where H = string(holding_cost_pct * unit_cost)
        """
        try:
            if annual_demand < 0 or setup_ordering_cost < 0 or unit_cost <= 0:
                return Err(ValueError("Demand, setup cost, and unit cost must be strictly positive vectors"))
                
            if self.holding_cost_pct <= 0:
                return Err(ValueError("Holding cost percentage must be > 0"))
                
            holding_cost = self.holding_cost_pct * unit_cost
            eoq_float = math.sqrt((2 * annual_demand * setup_ordering_cost) / holding_cost)
            
            # Floor or ceil depending on logistics, mathematically we round to nearest whole unit
            eoq_units = int(round(eoq_float))
            return Ok(eoq_units)
            
        except Exception as e:
            return Err(e)

    def compute_reorder_point(self, annual_demand: int, lead_time_days: int, safety_stock_units: int = 0) -> Result[int, Exception]:
        """
        Calculates the Reorder Point (ROP).
        Formula: ROP = Lead Time Demand + Safety Stock
        Lead Time Demand = Average Daily Sales * Lead Time Days
        """
        try:
            if annual_demand < 0 or lead_time_days < 0 or safety_stock_units < 0:
                return Err(ValueError("Demand, lead time, and safety stock cannot be negative"))
            
            if self.operating_days_per_year <= 0:
                return Err(ValueError("Operating days must be strictly > 0"))

            avg_daily_demand = annual_demand / self.operating_days_per_year
            lead_time_demand = avg_daily_demand * lead_time_days
            
            rop = int(round(lead_time_demand + safety_stock_units))
            return Ok(rop)
            
        except Exception as e:
            return Err(e)

    def generate_procurement_target(
        self, annual_demand: int, setup_ordering_cost: float, unit_cost: float, lead_time_days: int, safety_stock_units: int = 0
    ) -> Result[Dict[str, Any], Exception]:
        """
        Produces a complete procurement logistics envelope for an SKU.
        """
        try:
            eoq_res = self.compute_eoq(annual_demand, setup_ordering_cost, unit_cost)
            if not eoq_res.is_ok():
                return Err(eoq_res.unwrap_err())
                
            rop_res = self.compute_reorder_point(annual_demand, lead_time_days, safety_stock_units)
            if not rop_res.is_ok():
                return Err(rop_res.unwrap_err())
                
            eoq = eoq_res.unwrap()
            rop = rop_res.unwrap()
            
            optimal_orders_per_year = annual_demand / max(eoq, 1)
            
            target = {
                "economic_order_quantity": eoq,
                "reorder_point": rop,
                "annual_demand": annual_demand,
                "lead_time_days": lead_time_days,
                "safety_stock": safety_stock_units,
                "optimal_orders_per_year": round(optimal_orders_per_year, 2),
                "frequency_days": round(self.operating_days_per_year / max(optimal_orders_per_year, 1), 2)
            }
            return Ok(target)
            
        except Exception as e:
            return Err(e)
