# OMNI Compute Layer - TGI Continuous Batcher
class TGIError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def evaluate_batch_step(active_requests: list, max_batch_size: int) -> Result:
    """TGI continuous iteration step, adding new requests and dropping finished ones."""
    try:
        if not active_requests:
            return Result(error=TGIError("No active requests"))
            
        current_size = len(active_requests)
        can_accept_more = current_size < max_batch_size
        
        # Simulate processing step
        finished_ids = [req['id'] for req in active_requests if req.get('tokens_left', 0) <= 1]
        
        return Result(value={"finished_requests": finished_ids, "can_accept": can_accept_more})
    except Exception as e:
        return Result(error=TGIError(f"Batch step failed: {str(e)}"))
