from typing import Any, Dict, List, Set
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniPracticeGitProgrammingCoursesEngine:
    """
    Engine for resolving directed acyclic commit graphs.
    Implements pure logic without stochastic properties.
    """
    def __init__(self) -> None:
        self.commits: Dict[str, List[str]] = {}

    def commit(self, hash_id: str, parents: List[str]) -> Result[bool, str]:
        """Perform commit computation.

            Args:
                    hash_id: str
                    parents: List[str]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not hash_id or hash_id in self.commits:
            return Err("Invalid or duplicate commit hash")
            
        for p in parents:
            if p not in self.commits:
                return Err(f"Parent commit not found: {p}")
                
        self.commits[hash_id] = parents
        return Ok(True)

    def resolve_ancestry(self, hash_id: str) -> Result[Set[str], str]:
        """Perform resolve ancestry computation.

            Args:
                    hash_id: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if hash_id not in self.commits:
            return Err("Commit not found")
            
        visited = set()
        stack = [hash_id]
        
        while stack:
            curr = stack.pop()
            if curr not in visited:
                visited.add(curr)
                stack.extend(self.commits[curr])
                
        return Ok(visited)

    def calculate_merge_distance(self, hash_a: str, hash_b: str) -> Result[int, str]:
        """Perform calculate merge distance computation.

            Args:
                    hash_a: str
                    hash_b: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        ancestry_a = self.resolve_ancestry(hash_a)
        if not ancestry_a.is_ok(): return Err(ancestry_a.error)
        
        ancestry_b = self.resolve_ancestry(hash_b)
        if not ancestry_b.is_ok(): return Err(ancestry_b.error)
        
        common = ancestry_a.unwrap().intersection(ancestry_b.unwrap())
        if not common:
            return Err("No common ancestor found")
            
        distance = len(ancestry_a.unwrap()) + len(ancestry_b.unwrap()) - 2 * len(common)
        return Ok(distance)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "commit_count": len(self.commits),
            "engine": "OmniPracticeGitProgrammingCoursesEngine"
        }
