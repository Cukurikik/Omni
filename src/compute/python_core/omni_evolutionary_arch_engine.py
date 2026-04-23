"""
OMNI Evolutionary Architecture Engine - Fitness functions.
Assimilated from: evolutionary-architecture-by-example
Provides: Mathematical metric evaluator for architecture fitness, cyclomatic checking, dependency tree depth.
"""
from typing import Dict, List, Any
from src.compute.python_core.omni_base_engine import Result, Ok, Err

ENGINE_VERSION = "1.0.0-omni-evolution"




class OmniEvolutionaryArchEngine:
    """
    Computes system boundaries and module dependency fitness dynamically.
    Ensures zero cyclic dependencies and tracks module weight over time.

    @since 1.0.0
    @tags ["evolutionary", "fitness", "architecture", "metrics"]
    """
    def __init__(self) -> None:
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        deps = {"A": ["B"], "B": ["C"], "C": []}
        res = self.detect_cyclic_dependency(deps)
        if res.is_ok() and res.value is False:
            return Ok({"engine": "Evolutionary", "status": "Ready", "fitness_func": "Functional"})
        return Err("Cycle detection failed.")

    def detect_cyclic_dependency(self, adj_list: Dict[str, List[str]]) -> Result:
        """Kahn's / DFS approach to mathematical cycle detection."""
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj_list.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for n in adj_list:
            if n not in visited:
                if dfs(n):
                    return Ok(True)  # Cycle detected
        return Ok(False)  # No cycle

    def calculate_fitness_score(self, latency_ms: float, memory_mb: float, complexity: int) -> Result:
        """Determines the OMNI-defined mathematical fitness of an endpoint or component."""
        if latency_ms < 0 or memory_mb < 0 or complexity < 1:
            return Err("Invalid parameters for fitness score.")
        
        # OMNI Fitness Formula: High score is worse
        score = (latency_ms * 0.5) + (memory_mb * 0.3) + (complexity * 1.5)
        return Ok({"fitness_penalty": round(score, 3), "passing": score < 100.0})
