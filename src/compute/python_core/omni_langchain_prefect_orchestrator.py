# Omni Langchain-Prefect Task Orchestrator (Python)
# Ref: prefect-archive/langchain-prefect
from typing import List, Dict

def create_flow(name: str, tasks: List[Dict]) -> Dict:
    return {"name": name, "tasks": [{"id": i, **t, "status": "pending"} for i, t in enumerate(tasks)],
            "status": "created"}

def execute_flow(flow: Dict) -> Dict:
    completed = 0
    for task in flow["tasks"]:
        task["status"] = "completed"; completed += 1
    flow["status"] = "completed" if completed == len(flow["tasks"]) else "partial"
    return flow

def retry_failed(flow: Dict, max_retries: int = 3) -> Dict:
    for task in flow["tasks"]:
        if task["status"] == "failed":
            retries = task.get("retries", 0)
            if retries < max_retries:
                task["status"] = "pending"; task["retries"] = retries + 1
    return flow
