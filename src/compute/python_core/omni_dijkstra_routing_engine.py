import datetime
import heapq
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniDijkstraRoutingEngine:
    """
    OmniDijkstraRoutingEngine
    Batch: 28 (Semester 10)
    
    A zero-mock graph theoretical engine that computes the deterministic
    shortest-path routing topologies for distributed systems logic networks.
    """
    
    def __init__(self, adjacency_list: Dict[str, Dict[str, float]]):
        """
        :param adjacency_list: Graph representation e.g. {"A": {"B": 1.5, "C": 2.0}, "B": {"C": 0.5}}
        """
        self.graph = adjacency_list

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "nodes": list(self.graph.keys()),
            "edges_count": sum(len(edges) for edges in self.graph.values()),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def compute_shortest_path(self, start_node: str, target_node: str) -> Result[Dict[str, Any], Exception]:
        """
        Calculates the absolute shortest scalar path between two nodes and constructs
        the exact traversal vector sequence.
        """
        try:
            if start_node not in self.graph:
                return Err(ValueError(f"Start node '{start_node}' not found in graph"))
            if target_node not in self.graph:
                return Err(ValueError(f"Target node '{target_node}' not found in graph"))
                
            distances = {n: float('inf') for n in self.graph}
            distances[start_node] = 0.0
            
            # parent mapping for trace reconstruction
            parents = {n: None for n in self.graph}
            
            priority_queue = [(0.0, start_node)]
            
            while priority_queue:
                current_dist, current_node = heapq.heappop(priority_queue)
                
                # Prune obsolete queue entries
                if current_dist > distances[current_node]:
                    continue
                    
                if current_node == target_node:
                    break
                    
                for neighbor, weight in self.graph.get(current_node, {}).items():
                    if neighbor not in distances:
                         return Err(ValueError(f"Invalid edge destination '{neighbor}' not declared as node"))
                    if weight < 0:
                        return Err(ValueError(f"Negative edge weights prohibited in target node '{neighbor}'"))
                        
                    distance = current_dist + weight
                    
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        parents[neighbor] = current_node
                        heapq.heappush(priority_queue, (distance, neighbor))
            
            if distances[target_node] == float('inf'):
                return Err(RuntimeError(f"No valid path exists between '{start_node}' and '{target_node}'"))
                
            # Reconstruct Path
            path = []
            curr = target_node
            while curr is not None:
                path.insert(0, curr)
                curr = parents[curr]
                
            return Ok({
                "start": start_node,
                "target": target_node,
                "reachable": True,
                "total_cost": round(distances[target_node], 4),
                "path_vector": path,
                "hops": len(path) - 1
            })
            
        except Exception as e:
            return Err(e)

    def evaluate_reachability(self, start_node: str) -> Result[Dict[str, float], Exception]:
        """
        Computes shortest distances to all reachable nodes from a single origin structure.
        """
        try:
            if start_node not in self.graph:
                return Err(ValueError(f"Start node '{start_node}' not found in graph"))
                
            distances = {n: float('inf') for n in self.graph}
            distances[start_node] = 0.0
            priority_queue = [(0.0, start_node)]
            
            while priority_queue:
                current_dist, current_node = heapq.heappop(priority_queue)
                
                if current_dist > distances[current_node]:
                    continue
                    
                for neighbor, weight in self.graph.get(current_node, {}).items():
                    if neighbor not in distances:
                         return Err(ValueError(f"Invalid edge destination '{neighbor}' not declared as node"))
                    if weight < 0:
                        return Err(ValueError(f"Negative edge weights prohibited in target node '{neighbor}'"))
                        
                    distance = current_dist + weight
                    
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        heapq.heappush(priority_queue, (distance, neighbor))
                        
            # Filter unreachable
            reachable = {n: round(dist, 4) for n, dist in distances.items() if dist != float('inf')}
            
            return Ok(reachable)
            
        except Exception as e:
            return Err(e)
