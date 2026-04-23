from typing import Dict, Any, List, Set
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniSoftwareArchDesignEngine(OmniBaseEngine):
    """
    Evaluates topological layer constraints, determining architectural
    purity, circular dependency violation, and coupling indexes.
    """
    
    def __init__(self):
        super().__init__()
        self.components: Dict[str, List[str]] = {}

    def register_component(self, name: str) -> Result[bool, str]:
        """Perform register component computation.

            Args:
                    name: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if name in self.components:
            return Result.fail(f"Component boundary already resolved: '{name}'")
        self.components[name] = []
        return Result.ok(True)

    def add_dependency(self, source: str, target: str) -> Result[bool, str]:
        """
        Injects a structural coupling line between modules.
        """
        if source not in self.components or target not in self.components:
            return Result.fail("Violation: Entities must be explicitly registered.")
            
        if target in self.components[source]:
            return Result.fail("Structural topology redundancy map detected.")
            
        self.components[source].append(target)
        
        # Verify cycles
        cycle_res = self.detect_cycles()
        if not cycle_res.is_ok():
            # Error mapping, revert state
            self.components[source].remove(target)
            return Result.fail(f"Cyclic dependency blocked: {cycle_res.error}")
            
        return Result.ok(True)

    def detect_cycles(self) -> Result[bool, str]:
        """
        Determines directed cyclic chains via topological graph deep-search.
        """
        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.components.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for comp in self.components:
            if comp not in visited:
                if dfs(comp):
                    return Result.fail("Architectural hierarchy breached by circular coupling.")
                    
        return Result.ok(False)

    def compute_coupling_factor(self) -> Result[float, str]:
        """
        Evaluates system tightness constraints.
        """
        n = len(self.components)
        if n == 0:
            return Result.ok(0.0)
            
        total_edges = sum(len(deps) for deps in self.components.values())
        max_possible = n * (n - 1)
        
        factor = total_edges / max_possible if max_possible > 0 else 0.0
        return Result.ok(factor)

    def diagnostics(self) -> dict:
        """Return engine diagnostic metadata.

        Returns:
            dict: Engine name, version, and operational status.
        """
        return {"engine": "OmniSoftwareArchDesignEngine", "version": "1.0.0", "status": "operational"}
