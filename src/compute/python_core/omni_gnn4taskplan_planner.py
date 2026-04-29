# Omni GNN4TaskPlan Planner (Python)
# Compute Layer: Graph neural network enhanced task planning for LLM agents.
# Ref: WxxShirley/GNN4TaskPlan — NeurIPS 2024, Graph Learning for Planning.

from typing import List, Dict, Tuple, Set
import math

class TaskNode:
    __slots__ = ('task_id', 'description', 'dependencies', 'embedding')
    def __init__(self, task_id: str, description: str, dependencies: List[str], embedding: List[float]):
        self.task_id = task_id
        self.description = description
        self.dependencies = dependencies
        self.embedding = embedding

def topological_sort(nodes: List[TaskNode]) -> List[str]:
    graph: Dict[str, Set[str]] = {n.task_id: set(n.dependencies) for n in nodes}
    result: List[str] = []
    visited: Set[str] = set()
    temp: Set[str] = set()
    def dfs(node: str) -> bool:
        if node in temp: return False
        if node in visited: return True
        temp.add(node)
        for dep in graph.get(node, set()):
            if not dfs(dep): return False
        temp.discard(node)
        visited.add(node)
        result.append(node)
        return True
    for n in graph:
        if n not in visited:
            if not dfs(n): return []
    return result

def cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or not a: return 0.0
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0: return 0.0
    return round(dot / (na * nb), 8)
