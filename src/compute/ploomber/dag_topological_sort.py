from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque

# OMNI Ploomber - DAG Topological Sort
# Pure Python implementation of Kahn's Algorithm with monadic error propagation

class DAGExecutor:
    def __init__(self, edges: List[Tuple[str, str]]):
        self.adj_list = defaultdict(list)
        self.in_degree = defaultdict(int)
        self.nodes = set()
        
        for u, v in edges:
            self.adj_list[u].append(v)
            self.in_degree[v] += 1
            self.nodes.add(u)
            self.nodes.add(v)
            if u not in self.in_degree:
                self.in_degree[u] = 0

    def get_execution_order(self) -> Tuple[Optional[List[str]], Optional[Exception]]:
        try:
            queue = deque([u for u in self.nodes if self.in_degree[u] == 0])
            sorted_order = []
            visited_count = 0
            
            while queue:
                u = queue.popleft()
                sorted_order.append(u)
                visited_count += 1
                
                for v in self.adj_list[u]:
                    self.in_degree[v] -= 1
                    if self.in_degree[v] == 0:
                        queue.append(v)
            
            if visited_count != len(self.nodes):
                return None, ValueError("Cycle detected in DAG. Topological sort impossible.")
                
            return sorted_order, None
        except Exception as e:
            return None, e
