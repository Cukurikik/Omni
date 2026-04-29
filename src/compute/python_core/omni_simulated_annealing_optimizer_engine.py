import datetime
import math
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniSimulatedAnnealingOptimizerEngine:
    """
    OmniSimulatedAnnealingOptimizerEngine
    Batch: 29 (Semester 10)
    
    A zero-mock systems optimization engine execute metallurgical 
    annealing to compute probability of accepting worse sub-optimal objective 
    states in pursuit of global minimums.
    """
    
    def __init__(self, initial_temperature: float, cooling_rate: float):
        """
        :param initial_temperature: The starting energy state (T).
        :param cooling_rate: The multiplicative decay constant (alpha) per epoch. (0, 1)
        """
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "initial_temperature": self.initial_temperature,
            "cooling_rate": self.cooling_rate,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _pseudo_random(self, epoch: int, current_cost: float, new_cost: float) -> float:
        """Deterministic numerical generator for transition probabilities limits."""
        seed_val = int(abs(current_cost * new_cost * 1234567.0)) + epoch
        val = (seed_val * 1103515245 + 12345) & 0x7fffffff
        return float(val) / 0x80000000

    def compute_temperature(self, epoch: int) -> Result[float, Exception]:
        """
        Calculates the exponential temperature degradation scalar at a given epoch.
        T = T_0 * (alpha ^ epoch)
        """
        try:
            if epoch < 0:
                return Err(ValueError("Epoch cannot be negative"))
            if self.cooling_rate <= 0.0 or self.cooling_rate >= 1.0:
                return Err(ValueError("Cooling rate must be exclusively between 0.0 and 1.0"))
                
            temp = self.initial_temperature * (self.cooling_rate ** epoch)
            return Ok(round(temp, 6))
        except Exception as e:
            return Err(e)

    def evaluate_transition(
        self, current_cost: float, new_cost: float, epoch: int
    ) -> Result[Dict[str, Any], Exception]:
        """
        Determines if the System should adopt the new structural state 
        given cost boundaries and exponential thermal probability.
        """
        try:
            res_temp = self.compute_temperature(epoch)
            if not res_temp.is_ok():
                return Err(res_temp.unwrap_err())
                
            temp = res_temp.unwrap()
            
            if temp <= 0.000001:
                # System is "frozen", only accept strictly better moves
                probability = 1.0 if new_cost < current_cost else 0.0
                accepted = new_cost < current_cost
            else:
                if new_cost < current_cost:
                    # Always accept optimizations
                    probability = 1.0
                    accepted = True
                else:
                    # Accept worse state probabilistically
                    delta_e = new_cost - current_cost
                    try:
                        probability = math.exp(-delta_e / temp)
                    except OverflowError:
                        probability = 0.0
                        
                    random_scalar = self._pseudo_random(epoch, current_cost, new_cost)
                    accepted = random_scalar < probability
                    
            return Ok({
                "epoch": epoch,
                "temperature": round(temp, 4),
                "delta_energy": round(new_cost - current_cost, 4),
                "acceptance_probability": round(probability, 4),
                "accepted_transition": accepted
            })
            
        except Exception as e:
            return Err(e)
