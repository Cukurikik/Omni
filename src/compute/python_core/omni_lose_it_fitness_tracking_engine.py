from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniLoseItFitnessTrackingEngine:
    """
    omni-lose-it-fitness-tracking
    
    Models native structural mathematical bounds allocating basal metabolic rates (BMR) 
    and rolling array caloric matrix averages natively.
    """
    
    ENGINE_VERSION = "omni-s11-b6.1.0"
    
    def __init__(self, basal_metabolic_rate: float = 2000.0) -> None:
        self.bmr = basal_metabolic_rate

    def calculate_rolling_caloric_balance(self, daily_intakes: List[float], daily_expenditures: List[float]) -> Result:
        """
        Takes raw limits geometries natively mapping limits boundary.
        Calculates daily delta natively constraints.
        """
        try:
            if not daily_intakes or not daily_expenditures:
                return Err(ValueError("Cannot computationally sequence numeric limits on empty structural matrix vectors."))
                
            if len(daily_intakes) != len(daily_expenditures):
                return Err(ValueError("Structural boundaries require matching dimension logic limits."))
                
            total_days = len(daily_intakes)
            running_balance = 0.0
            
            # Mathematical boundaries
            daily_deltas = []
            
            for i in range(total_days):
                intake = daily_intakes[i]
                active_expend = daily_expenditures[i]
                
                # Math bounds
                net = intake - (self.bmr + active_expend)
                running_balance += net
                daily_deltas.append(round(net, 2))
                
            average_daily = running_balance / total_days
            
            return Ok({
                "rolling_deltas_matrix": daily_deltas,
                "cumulative_balance": round(running_balance, 2),
                "average_net_daily": round(average_daily, 2),
                "trajectory": "WEIGHT_LOSS" if running_balance < 0 else "WEIGHT_GAIN" if running_balance > 0 else "MAINTENANCE"
            })
            
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides internal tracking limit matrices bounds."""
        return {
            "engine": "OmniLoseItFitnessTrackingEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "reference_bmr": self.bmr,
            "complexity": "O(N) Sequential Float Arrays Bounding"
        }
