from typing import Dict, List

class DAGParser:
    def compute_max_depth(self, adjacency_list: Dict[str, List[str]]) -> int:
        memo = {}
        
        def dfs(node, visited):
            if node in visited:
                raise ValueError("Cycle detected in DAG")
            if node in memo:
                return memo[node]
                
            visited.add(node)
            max_child_depth = 0
            for child in adjacency_list.get(node, []):
                max_child_depth = max(max_child_depth, dfs(child, visited))
            visited.remove(node)
            
            memo[node] = 1 + max_child_depth
            return memo[node]
            
        max_depth = 0
        for node in adjacency_list:
            max_depth = max(max_depth, dfs(node, set()))
            
        return max_depth
