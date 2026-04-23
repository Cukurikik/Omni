import datetime
import math
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMarketMakingSpreadEngine:
    """
    OmniMarketMakingSpreadEngine
    Batch: 27 (Semester 10)
    
    A zero-mock financial engine that computes bid and ask quotes
    with spread scaling based on volatility, order book position, 
    and target inventory constraints.
    """
    
    def __init__(self, target_inventory: int, risk_aversion_gamma: float):
        self.target_inventory = target_inventory
        self.gamma = risk_aversion_gamma

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "gamma": self.gamma,
            "target_inventory": self.target_inventory,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def compute_reservation_price(
        self, mid_price: float, current_inventory: int, volatility: float, time_t: float
    ) -> Result[float, Exception]:
        """
        Computes the reservation (indifference) price via Avellaneda-Stoikov dynamics.
        R = S_mid - q * gamma * sigma^2 * T
        """
        try:
            if mid_price <= 0:
                return Err(ValueError("Mid price must be > 0"))
            if volatility < 0:
                return Err(ValueError("Volatility must be non-negative"))
            if time_t <= 0:
                return Err(ValueError("Time parameter must be strictly positive"))
                
            q = current_inventory - self.target_inventory
            # We treat time_t as remaining time 
            r_price = mid_price - (q * self.gamma * (volatility ** 2) * time_t)
            return Ok(round(r_price, 4))
        except Exception as e:
            return Err(e)

    def compute_quotes(
        self, mid_price: float, current_inventory: int, volatility: float, time_t: float, spread_k: float
    ) -> Result[Dict[str, float], Exception]:
        """
        Computes the target bid/ask quotes adding spread (spread_k) distributed around the reservation price.
        """
        try:
            res_val = self.compute_reservation_price(mid_price, current_inventory, volatility, time_t)
            if not res_val.is_ok():
                return Err(res_val.unwrap_err())
                
            reservation_price = res_val.unwrap()
            
            # Spread bounds symmetrically from reservation price
            half_spread = (self.gamma * (volatility ** 2) * time_t) + (1.0 / spread_k) * math.log(1.0 + (self.gamma / spread_k))
            # Just approximate generic spread scaling
            half_spread = half_spread if half_spread > 0 else spread_k
            
            bid = round(reservation_price - half_spread, 4)
            ask = round(reservation_price + half_spread, 4)
            
            # Cap/Floor safeguards
            if bid >= ask:
                bid = reservation_price - 0.01
                ask = reservation_price + 0.01
                
            return Ok({
                "mid_price": mid_price,
                "reservation_price": reservation_price,
                "bid": bid,
                "ask": ask,
                "spread": round(ask - bid, 4),
                "skew": round(reservation_price - mid_price, 4)
            })
            
        except Exception as e:
            return Err(e)
