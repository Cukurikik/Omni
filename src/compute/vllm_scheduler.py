# OMNI Compute Layer - vLLM Scheduler
class SchedulerError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def schedule_batch(requests: list, available_blocks: int) -> Result:
    """Schedules a batch of LLM requests using continuous batching."""
    try:
        if not requests:
            return Result(error=SchedulerError("No requests to schedule"))
            
        scheduled = []
        blocks_used = 0
        for req in requests:
            if blocks_used + req['blocks'] <= available_blocks:
                scheduled.append(req['id'])
                blocks_used += req['blocks']
                
        return Result(value={"scheduled_ids": scheduled, "blocks_used": blocks_used})
    except Exception as e:
        return Result(error=SchedulerError(f"Scheduling failed: {str(e)}"))
