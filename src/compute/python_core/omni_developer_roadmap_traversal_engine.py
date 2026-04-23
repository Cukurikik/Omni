from __future__ import annotations
from typing import Dict, Any, List, Set
from collections import defaultdict, deque
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniDeveloperRoadmapTraversalEngine:
    """
    omni-developer-roadmap-traversal
    
    A structural mathematical DAG solver natively identifying course prerequisite 
    chain barriers utilizing topological sorting bounds without dependencies.
    Inspired by marcieltorres/become-a-developer.
    """
    
    ENGINE_VERSION = "omni-s11-b4.1.0"
    
    def __init__(self) -> None:
        pass

    def traverse_curriculum_dag(self, elements: List[str], dependencies: List[tuple[str, str]]) -> Result:
        """
        Takes raw string topics and standard (prerequisite -> topic) dependencies.
        Returns exact linear learning path using Kahn's topological structure mathematically.
        """
        try:
            if not elements:
                return Err(ValueError("Cannot map empty DAG structure"))
                
            in_degree = {element: 0 for element in elements}
            graph = defaultdict(list)
            
            for index, (u, v) in enumerate(dependencies):
                if u not in in_degree or v not in in_degree:
                    return Err(ValueError(f"DAG Edge Index {index} refers to unbound elements in element matrix: {u} -> {v}"))
                graph[u].append(v)
                in_degree[v] += 1
                
            queue = deque([node for node in in_degree if in_degree[node] == 0])
            traversed_matrix = []
            
            while queue:
                current_node = queue.popleft()
                traversed_matrix.append(current_node)
                
                for neighbor in graph[current_node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
                        
            # Check for cyclical loop bounds
            if len(traversed_matrix) != len(elements):
                return Err(ValueError("Cyclical dependency detected. Curriculum graph is mathematically unsolvable."))
            
            return Ok({
                "path": traversed_matrix,
                "complexity": len(traversed_matrix),
                "isolated_branches": len([node for node in graph if not graph[node]])
            })
            
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Framework adherence metrics."""
        return {
            "engine": "OmniDeveloperRoadmapTraversalEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "complexity": "O(V + E) Topological Sort"
        }
