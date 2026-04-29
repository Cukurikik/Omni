# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Marimo Reactive DAG (OMNI Zero-Mock Implementation)
# Implements directed acyclic graph topological sorting for notebooks.

from dataclasses import dataclass
from typing import List, Dict, Set, Optional

@dataclass
class Result:
    value: Optional[List[str]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[str]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class MarimoGraphRouter:
    def _dfs(self, node: str, graph: Dict[str, List[str]], visited: Set[str], 
             recursion_stack: Set[str], order: List[str]) -> bool:
        visited.add(node)
        recursion_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if self._dfs(neighbor, graph, visited, recursion_stack, order):
                    return True
            elif neighbor in recursion_stack:
                return True # Cycle detected
                
        recursion_stack.remove(node)
        order.append(node)
        return False

    def solve_execution_order(self, cell_dependencies: Dict[str, List[str]]) -> Result:
        if not cell_dependencies:
            return Result.err("Dependency graph is empty.")
            
        visited = set()
        recursion_stack = set()
        order = []
        
        for node in cell_dependencies.keys():
            if node not in visited:
                has_cycle = self._dfs(node, cell_dependencies, visited, recursion_stack, order)
                if has_cycle:
                    return Result.err(f"Cycle detected in reactive DAG starting from cell: {node}")
                    
        # Reverse to get proper topological order
        return Result.ok(order[::-1])
