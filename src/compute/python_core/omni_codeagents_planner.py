# Omni CodeAgents Planner Engine
from typing import List, Dict

def generate_code_execution_plan(task_description: str, available_tools: List[str]) -> List[Dict[str, str]]:
    """Generate a deterministic static execution plan for a coding agent."""
    plan = []
    task = task_description.lower()
    
    if "read" in task or "find" in task:
        if "grep_search" in available_tools:
            plan.append({"tool": "grep_search", "intent": "locate relevant code"})
    
    if "write" in task or "create" in task:
        if "write_to_file" in available_tools:
            plan.append({"tool": "write_to_file", "intent": "create base file"})
            
    if "update" in task or "modify" in task:
        if "replace_file_content" in available_tools:
            plan.append({"tool": "replace_file_content", "intent": "patch existing code"})
            
    return plan

def evaluate_plan_completeness(plan: List[Dict[str, str]], required_intents: List[str]) -> float:
    if not required_intents:
        return 1.0
    intents_found = sum(1 for req in required_intents if any(req in step["intent"] for step in plan))
    return round(intents_found / len(required_intents), 4)
