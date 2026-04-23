import datetime
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniTokenBucketRateLimitEngine:
    """
    OmniTokenBucketRateLimitEngine
    Batch: 27 (Semester 10)
    
    A zero-mock precision token bucket rate limiting mathematical engine.
    Calculates exact token fills using continuous temporal progression 
    and checks depletion constraint boundaries.
    """
    
    def __init__(self, capacity: float, fill_rate_per_sec: float):
        """
        :param capacity: Max burst token limit.
        :param fill_rate_per_sec: Tokens generated per second.
        """
        self.capacity = capacity
        self.fill_rate = fill_rate_per_sec

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "capacity": self.capacity,
            "fill_rate": self.fill_rate,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def compute_request_allowance(
        self, 
        current_tokens: float, 
        last_fill_timestamp: float, 
        current_timestamp: float, 
        tokens_requested: float = 1.0
    ) -> Result[Dict[str, Any], Exception]:
        """
        Computes if a request is allowed and yields the updated state.
        Temporal progression calculates accurate continuous fills.
        """
        try:
            if current_timestamp < last_fill_timestamp:
                return Err(ValueError("Current timestamp cannot be strictly before last fill timestamp"))
                
            if current_tokens < 0.0 or tokens_requested <= 0.0:
                return Err(ValueError("Current tokens must be >= 0 and requested tokens > 0"))
                
            time_delta = current_timestamp - last_fill_timestamp
            fill_amount = time_delta * self.fill_rate
            
            # Add fill and clamp to max capacity
            replenished_tokens = min(current_tokens + fill_amount, self.capacity)
            
            # Check depletion bound
            if replenished_tokens >= tokens_requested:
                granted = True
                new_tokens = replenished_tokens - tokens_requested
            else:
                granted = False
                new_tokens = replenished_tokens
                
            return Ok({
                "granted": granted,
                "new_token_balance": round(new_tokens, 4),
                "tokens_requested": tokens_requested,
                "tokens_generated_in_delta": round(fill_amount, 4),
                "new_timestamp": current_timestamp
            })
            
        except Exception as e:
            return Err(e)

    def calculate_wait_time(self, current_tokens: float, tokens_requested: float) -> Result[float, Exception]:
        """
        Given a rejected request, calculates exactly how many seconds until it will be granted
        assuming zero other competing requests.
        """
        try:
            if current_tokens < 0.0 or tokens_requested <= 0.0:
                return Err(ValueError("Current tokens must be >= 0 and requested tokens > 0"))
                
            if tokens_requested > self.capacity:
                # Can never be fulfilled
                return Ok(float("inf"))
                
            if current_tokens >= tokens_requested:
                return Ok(0.0)
                
            deficit = tokens_requested - current_tokens
            wait_time = deficit / self.fill_rate
            return Ok(round(wait_time, 4))
            
        except Exception as e:
            return Err(e)
