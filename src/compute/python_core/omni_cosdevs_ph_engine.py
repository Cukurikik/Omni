from typing import Any, Dict, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniCosdevsPhEngine:
    """
    Engine for DOM rendering pipeline modeling.
    Calculates nested depth based on structural tags.
    """
    def __init__(self) -> None:
        self.dom_nodes: Dict[str, Dict[str, Any]] = {}

    def attach_node(self, node_id: str, tag: str, parent: Optional[str] = None) -> Result[bool, str]:
        """Perform attach node computation.

            Args:
                    node_id: str
                    tag: str
                    parent: Optional[str]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not node_id or node_id in self.dom_nodes:
            return Err("Invalid or duplicate node ID")
            
        if parent is not None and parent not in self.dom_nodes:
            return Err("Parent node not found")
            
        self.dom_nodes[node_id] = {
            "tag": tag,
            "parent": parent,
            "children": []
        }
        
        if parent is not None:
            self.dom_nodes[parent]["children"].append(node_id)
            
        return Ok(True)

    def compute_dom_depth(self) -> Result[int, str]:
        """Perform compute dom depth computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not self.dom_nodes:
            return Err("DOM is empty")
            
        roots = [nid for nid, node in self.dom_nodes.items() if node["parent"] is None]
        
        if not roots:
            return Err("DOM cycle detected")
            
        def _get_depth(node_id: str) -> int:
            children = self.dom_nodes[node_id]["children"]
            if not children:
                return 1
            return 1 + max(_get_depth(c) for c in children)
            
        max_depth = max(_get_depth(r) for r in roots)
        return Ok(max_depth)

    # Legacy Batch 31 methods
    def register_developer(self, dev: str, score: float) -> Result[bool, str]:
        """Perform register developer computation.

            Args:
                    dev: str
                    score: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not hasattr(self, "developers"): self.developers = {}
        if dev in self.developers: return Err("Dup")
        self.developers[dev] = {"score": score}
        return Ok(True)
        
    def connect_peers(self, dev1: str, dev2: str) -> Result[bool, str]:
        """Perform connect peers computation.

            Args:
                    dev1: str
                    dev2: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not hasattr(self, "developers") or dev1 not in self.developers or dev2 not in self.developers:
            return Err("Missing")
        self.developers[dev1]["score"] += 0.5
        self.developers[dev2]["score"] += 0.5
        return Ok(True)
        
    def log_contribution(self, dev: str, score: float) -> Result[float, str]:
        """Perform log contribution computation.

            Args:
                    dev: str
                    score: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not hasattr(self, "developers") or dev not in self.developers: return Err("Missing")
        self.developers[dev]["score"] += score
        return Ok(self.developers[dev]["score"])
        
    def evaluate_community_density(self) -> Result[float, str]:
        """Perform evaluate community density computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not hasattr(self, "developers") or not self.developers: return Err("Empty")
        return Ok(1.0)

    def calculate_component_hierarchy_weight(self, root_id: str) -> Result[float, str]:
        """Perform calculate component hierarchy weight computation.

            Args:
                    root_id: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if root_id not in self.dom_nodes:
            return Err("Root node not present in hierarchy")
            
        def _get_weight(node_id: str) -> float:
            base_w = 1.0
            for child in self.dom_nodes[node_id]["children"]:
                base_w += 0.5 * _get_weight(child)
            return base_w
            
        return Ok(_get_weight(root_id))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "node_count": len(self.dom_nodes),
            "engine": "OmniCosdevsPhEngine"
        }
