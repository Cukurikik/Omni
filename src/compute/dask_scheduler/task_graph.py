from omni.core import Result, Ok, Err

class TaskGraph:
    def __init__(self):
        self.nodes = set()

    def add_task(self, task_id: str) -> Result[bool, ValueError]:
        if not task_id:
            return Err(ValueError("Invalid task ID"))
        self.nodes.add(task_id)
        return Ok(True)
