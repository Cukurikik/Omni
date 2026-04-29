class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class TokenBucket:
    def __init__(self):
        pass

    def compute_allowance(self, current_tokens: float, last_refill_time: float, current_time: float, refill_rate: float, burst_capacity: float) -> OmniResult:
        if refill_rate <= 0 or burst_capacity <= 0:
            return OmniResult(error="Rate and capacity must be strictly positive")
            
        if current_time < last_refill_time:
            return OmniResult(error="Current time cannot be before last refill time")

        # Deterministic Token Bucket Algorithm Math
        time_passed = current_time - last_refill_time
        tokens_to_add = time_passed * refill_rate
        
        new_tokens = current_tokens + tokens_to_add
        if new_tokens > burst_capacity:
            new_tokens = burst_capacity
            
        if new_tokens >= 1.0:
            # Consume 1 token and allow request
            return OmniResult(value={"allowed": True, "remaining_tokens": new_tokens - 1.0, "time": current_time})
        else:
            # Reject request, no tokens consumed
            return OmniResult(value={"allowed": False, "remaining_tokens": new_tokens, "time": current_time})
