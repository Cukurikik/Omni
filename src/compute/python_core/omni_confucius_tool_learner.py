# Omni Confucius Tool Learner (Python)
# Compute Layer: Iterative tool learning with introspection feedback, curriculum-based.
# Ref: mangopy/Confucius-tool-learning — AAAI 2024.

from typing import List, Dict, Tuple
import math

class ToolExperience:
    __slots__ = ('tool_name', 'difficulty', 'success', 'introspection')
    def __init__(self, tool_name: str, difficulty: float, success: bool, introspection: str):
        self.tool_name = tool_name
        self.difficulty = max(0.0, min(1.0, difficulty))
        self.success = success
        self.introspection = introspection

def sort_curriculum(experiences: List[ToolExperience]) -> List[ToolExperience]:
    return sorted(experiences, key=lambda e: e.difficulty)

def compute_mastery_score(experiences: List[ToolExperience]) -> float:
    if not experiences:
        return 0.0
    total_weight = 0.0
    weighted_success = 0.0
    for exp in experiences:
        w = exp.difficulty + 0.1
        total_weight += w
        if exp.success:
            weighted_success += w
    return round(weighted_success / total_weight, 6) if total_weight > 0 else 0.0

def select_next_tool(
    experiences: List[ToolExperience],
    available_tools: List[str]
) -> str:
    mastered = {e.tool_name for e in experiences if e.success}
    for tool in available_tools:
        if tool not in mastered:
            return tool
    return available_tools[0] if available_tools else ""
