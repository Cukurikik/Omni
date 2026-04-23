from typing import List, Dict, Set, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniSpkPackageManagerEngine:
    """
    OmniSpkPackageManagerEngine
    
    Level-2 Abstraction for high-velocity package management (assimilated from 'spkenv/spk').
    Provides strict mathematical validation of dependency paths, specifically 
    detecting and resolving circular dependencies within directed acyclic graphs (DAGs) 
    of software environments.
    """

    @classmethod
    def resolve_dependency_graph(cls, package_graph: Dict[str, List[str]]) -> Result[List[str], Exception]:
        """
        Calculates a topological sort of the provided dependency graph to 
        enforce strict DAG immutability and prevent circular dependencies.
        
        Args:
            package_graph: Dictionary mapping a package to its list of dependencies.
        
        Returns:
            Result[List[str], Exception]: Ok containing the linear installation sequence, 
            or Err if a cycle is detected.
        """
        # Calculate in-degrees
        in_degree: Dict[str, int] = {node: 0 for node in package_graph}
        for node, neighbors in package_graph.items():
            for neighbor in neighbors:
                if neighbor not in in_degree:
                    in_degree[neighbor] = 0
                in_degree[neighbor] += 1

        # Queue for nodes with 0 in-degree
        queue: List[str] = [node for node, degree in in_degree.items() if degree == 0]
        resolution_path: List[str] = []

        while queue:
            current = queue.pop(0)
            resolution_path.append(current)

            for neighbor in package_graph.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(resolution_path) == len(in_degree):
            # Reverse because dependencies need to be installed before the package that requires them
            return Ok(resolution_path[::-1])
        else:
            return Err(Exception(f"Circular dependency cycle detected in the package environment architecture. Detected size: {len(in_degree)}"))

    @classmethod
    def diagnostics(cls) -> Dict[str, str]:
        return {
            "status": "operational",
            "mode": "Zero-Prod Mathematical Execution",
            "layer": "System/System-Package",
            "rule": "Strict DAG Adherence"
        }
