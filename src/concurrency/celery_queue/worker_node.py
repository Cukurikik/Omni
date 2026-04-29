from omni.core import Result, Ok, Err

class WorkerNode:
    def consume(self, queue_name: str) -> Result[bool, ValueError]:
        if not queue_name:
            return Err(ValueError("Queue name empty"))
        return Ok(True)
