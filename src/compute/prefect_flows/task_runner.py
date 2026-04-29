from omni.core import Result, Ok, Err

class TaskRunner:
    def run_task(self, task_name: str) -> Result[str, ValueError]:
        if not task_name:
            return Err(ValueError("Task name empty"))
        return Ok(f"Task {task_name} completed")
