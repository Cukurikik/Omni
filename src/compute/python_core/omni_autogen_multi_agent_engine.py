"""
OMNI AutoGen Multi-Agent Engine
Message passing framework using directed acyclic graph reachability.
"""
from typing import Dict, Any, List
from collections import defaultdict, deque
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniAutoGenMultiAgentEngine(OmniBaseEngine):
    def __init__(self):
        super().__init__()

    def process(self, agent_transitions: List[Dict[str, str]], start_agent: str, target_agent: str) -> Result[List[str], str]:
        if not agent_transitions:
            return Err("Agent transitions map cannot be empty.")
            
        try:
            graph = defaultdict(list)
            for transition in agent_transitions:
                src = transition.get("source")
                dst = transition.get("destination")
                if not src or not dst:
                    return Err("Malformed transition payload.")
                graph[src].append(dst)
                
            queue = deque([[start_agent]])
            visited = set()
            
            while queue:
                path = queue.popleft()
                node = path[-1]
                
                if node == target_agent:
                    return Ok(path)
                    
                if node not in visited:
                    visited.add(node)
                    for adjacent in graph.get(node, []):
                        new_path = list(path)
                        new_path.append(adjacent)
                        queue.append(new_path)
                        
            return Err(f"No communication path exists between {start_agent} and {target_agent}")
        except Exception as e:
            return Err(f"DAG traversal failed: {str(e)}")

    def diagnostics(self) -> Result[Dict[str, Any], str]:
        edges = [{"source": "A", "destination": "B"}, {"source": "B", "destination": "C"}]
        res = self.process(edges, "A", "C")
        if hasattr(res, 'is_ok') and res.is_ok() and res.unwrap() == ["A", "B", "C"]:
            return Ok({"status": "healthy", "algorithm": "bfs_reachability"})
        return Err("Diagnostics failed on AutoGen engine.")
