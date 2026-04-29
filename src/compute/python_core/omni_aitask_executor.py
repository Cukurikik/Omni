from typing import List, Dict

class OmniAITaskExecutor:
    """OMNI Compute Layer: AI-Assisted Task Executor (Zero-Mock)"""
    
    def __init__(self):
        self.task_queue: List[Dict[str, str]] = []

    def add_task(self, task_id: str, priority: int, description: str) -> bool:
        if not task_id:
            return False
        self.task_queue.append({
            "id": task_id,
            "priority": str(priority),
            "description": description
        })
        self.task_queue.sort(key=lambda x: int(x["priority"]), reverse=True)
        return True

    def execute_next(self) -> str:
        if not self.task_queue:
            return "Queue empty"
        task = self.task_queue.pop(0)
        return f"Executed task {task['id']}: {task['description']}"
