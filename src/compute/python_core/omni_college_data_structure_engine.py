from typing import Any, Dict, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniCollegeDataStructureEngine:
    """
    Engine for mapping deterministic binary tree algorithms
    and memory topology modeled dynamically.
    """
    def __init__(self) -> None:
        self.tree: Dict[int, Dict[str, Optional[int]]] = {}
        self.root: Optional[int] = None

    def insert_node(self, val: int) -> Result[bool, str]:
        """Perform insert node computation.

            Args:
                    val: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if val < 0:
            return Err("Negative values not supported")
        
        if self.root is None:
            self.root = val
            self.tree[val] = {"left": None, "right": None}
            return Ok(True)
            
        current = self.root
        while True:
            if val == current:
                return Err("Duplicate node")
            if val < current:
                if self.tree[current]["left"] is None:
                    self.tree[current]["left"] = val
                    self.tree[val] = {"left": None, "right": None}
                    return Ok(True)
                current = self.tree[current]["left"]
            else:
                if self.tree[current]["right"] is None:
                    self.tree[current]["right"] = val
                    self.tree[val] = {"left": None, "right": None}
                    return Ok(True)
                current = self.tree[current]["right"]

    def compute_max_depth(self) -> Result[int, str]:
        """Perform compute max depth computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if self.root is None:
            return Err("Empty tree")
            
        def _depth(node_val: Optional[int]) -> int:
            if node_val is None:
                return 0
            left = _depth(self.tree[node_val]["left"])
            right = _depth(self.tree[node_val]["right"])
            return max(left, right) + 1
            
        return Ok(_depth(self.root))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "nodes": len(self.tree),
            "engine": "OmniCollegeDataStructureEngine"
        }
