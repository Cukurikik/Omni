from __future__ import annotations
from src.compute.python_core.omni_base_engine import Result, Ok, Err
from typing import Dict, Any, List, Set
import math

class OmniCareerPathTraversalEngine:
    """OMNI Zero-Prod Production Implementation for OmniCareerPathTraversalEngine."""
    
    def __init__(self) -> None:
        pass
        
    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniCareerPathTraversalEngine",
            "status": "operational",
            "batch": 53,
            "semester": 11,
            "domain": "DAG Skills Traversal Mathematics"
        }
        
    def find_shortest_skill_path(self, skill_graph: Dict[str, Dict[str, float]], start_node: str, end_node: str) -> Result:
        """
        Natively computed Dijkstra mapping over a weighted DAG representing career boundaries.
        Returns the minimized path payload natively.
        """
        try:
            if not skill_graph:
                return Err(ValueError("Career DAG mapping is structurally null"))
            if start_node not in skill_graph or end_node not in skill_graph:
                return Err(KeyError("Structural endpoints isolate out-of-bounds nodes"))
                
            distances = {node: math.inf for node in skill_graph}
            distances[start_node] = 0.0
            predecessors: Dict[str, str] = {}
            unvisited = set(skill_graph.keys())
            
            while unvisited:
                current = min(unvisited, key=lambda node: distances[node])
                if distances[current] == math.inf:
                    break  # Unreachable isolated nodes
                    
                if current == end_node:
                    break
                    
                unvisited.remove(current)
                
                for neighbor, weight in skill_graph[current].items():
                    if weight < 0:
                        return Err(ValueError("Mathematical impossibility: DAG path weight cannot be negative"))
                    if neighbor in unvisited:
                        new_dist = distances[current] + weight
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            predecessors[neighbor] = current
                            
            if distances[end_node] == math.inf:
                return Ok({"path": [], "total_weight": math.inf})
                
            # Reconstruct isolated boundary path natively
            path = []
            curr = end_node
            while curr != start_node:
                path.insert(0, curr)
                curr = predecessors[curr]
            path.insert(0, start_node)
            
            return Ok({"path": path, "total_weight": distances[end_node]})
        except Exception as e:
            return Err(e)
