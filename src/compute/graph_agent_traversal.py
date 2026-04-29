# OMNI Compute Layer - Graph Agent Traversal
class GraphError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def agent_traverse_graph(nodes: dict, edges: list, start_id: str) -> Result:
    """Executes agent-facilitated graph learning traversal."""
    try:
        if start_id not in nodes:
            return Result(error=GraphError("Start node not found in graph"))
            
        visited = set([start_id])
        queue = [start_id]
        
        while queue:
            curr = queue.pop(0)
            for edge in edges:
                if edge["source"] == curr and edge["target"] not in visited:
                    visited.add(edge["target"])
                    queue.append(edge["target"])
                    
        return Result(value={"reachable_nodes": list(visited), "count": len(visited)})
    except Exception as e:
        return Result(error=GraphError(f"Traversal failed: {str(e)}"))
