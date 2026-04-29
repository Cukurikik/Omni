# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Chip Huyen TF Tutorials (OMNI Zero-Mock Implementation)
# Implements Data Flow Graph static cycle detection.

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Result:
    value: Optional[bool] # True if acyclic (DAG), False if cycle exists
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: bool) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class TFGraphValidator:
    def validate_acyclic(self, nodes: List[str], adj_list: Dict[str, List[str]]) -> Result:
        if not nodes:
             return Result.err("Graph is empty.")
             
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            if node in adj_list:
                for neighbor in adj_list[node]:
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                        
            rec_stack.remove(node)
            return False
            
        for node in nodes:
            if node not in visited:
                if dfs(node):
                    return Result.ok(False) # Cycle found
                    
        return Result.ok(True) # Acyclic
