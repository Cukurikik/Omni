import datetime
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err



class OmniLeakyBucketRateLimitEngine:
    """
    OmniLeakyBucketRateLimitEngine
    Batch: 28 (Semester 10)
    
    A zero-mock flow control computing engine that processes requests 
    at a continuous fixed rate, accumulating overflows accurately.
    """
    
    def __init__(self, capacity: float, leak_rate_per_sec: float):
        """
        :param capacity: Max accumulation space before overflow discarding happens.
        :param leak_rate_per_sec: Steady rate at which the queue is drained.
        """
        self.capacity = capacity
        self.leak_rate = leak_rate_per_sec

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "capacity": self.capacity,
            "leak_rate_per_sec": self.leak_rate,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def compute_enqueue(
        self, 
        current_water_level: float, 
        last_check_timestamp: float, 
        current_timestamp: float, 
        request_size: float = 1.0
    ) -> Result[Dict[str, Any], Exception]:
        """
        Determines water level draining over time difference, adds request size,
        and bounds checks vs capacity constraint.
        """
        try:
            if current_timestamp < last_check_timestamp:
                return Err(ValueError("Time cannot flow backwards."))
                
            if current_water_level < 0.0 or request_size <= 0.0:
                return Err(ValueError("Water levels and request sizes must be strictly positive geometries."))
                
            elapsed = current_timestamp - last_check_timestamp
            leaked_amount = elapsed * self.leak_rate
            
            # Drain bucket (cannot go below 0)
            drained_level = max(0.0, current_water_level - leaked_amount)
            
            # Check overflow
            if drained_level + request_size <= self.capacity:
                accepted = True
                new_level = drained_level + request_size
                dropped = 0.0
            else:
                accepted = False
                new_level = drained_level
                dropped = request_size
                
            return Ok({
                "accepted": accepted,
                "drained_interval_amount": round(leaked_amount, 4),
                "new_water_level": round(new_level, 4),
                "dropped_volume": round(dropped, 4),
                "timestamp": current_timestamp
            })
            
        except Exception as e:
            return Err(e)

    def extract_drain_time(self, current_water_level: float) -> Result[float, Exception]:
        """
        Calculates time required to reach generic empty state holding queue elements.
        """
        try:
            if current_water_level <= 0.0:
                return Ok(0.0)
                
            drain_time = current_water_level / self.leak_rate
            return Ok(round(drain_time, 4))
        except Exception as e:
            return Err(e)
