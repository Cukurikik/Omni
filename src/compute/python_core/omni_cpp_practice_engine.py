from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniCppPracticeEngine:
    """
    A foundational deterministic tracker for low-level memory layout.
    """
    def __init__(self) -> None:
        self.allocations: Dict[str, int] = {}

    def malloc(self, ptr_id: str, size: int) -> Result[bool, str]:
        """Perform malloc computation.

            Args:
                    ptr_id: str
                    size: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not ptr_id or ptr_id in self.allocations:
            return Err("Invalid or duplicate pointer alias")
        if size <= 0:
            return Err("Allocation size must be positive")
            
        self.allocations[ptr_id] = size
        return Ok(True)

    def free(self, ptr_id: str) -> Result[bool, str]:
        """Perform free computation.

            Args:
                    ptr_id: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if ptr_id not in self.allocations:
            return Err("Segmentation Fault: pointer not mapped")
            
        del self.allocations[ptr_id]
        return Ok(True)

    def compute_memory_leak(self) -> Result[int, str]:
        """Perform compute memory leak computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        leak = sum(self.allocations.values())
        return Ok(leak)

    # Legacy Batch 31 methods
    def measure_memory_safety(self, ops: list) -> Result[Dict[str, Any], str]:
        """Perform measure memory safety computation.

            Args:
                    ops: list

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not ops: return Err("Empty")
        is_safe = True
        for op in ops:
            if "malloc" in op or "free" in op:
                is_safe = False
        return Ok({"is_safe": is_safe})
        
    def detect_dangling_pointers(self, ops: list) -> Result[int, str]:
        """Perform detect dangling pointers computation.

            Args:
                    ops: list

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        freed = set()
        dangling = 0
        for op in ops:
            if op["type"] == "FREE": freed.add(op["var"])
            elif op["type"] == "USE" and op["var"] in freed: dangling += 1
        return Ok(dangling)

    def calculate_pointer_entropy(self) -> Result[float, str]:
        """Perform calculate pointer entropy computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not self.allocations:
            return Err("No active allocations")
            
        total_size = sum(self.allocations.values())
        entropy = 0.0
        import math
        for size in self.allocations.values():
            prob = float(size) / float(total_size)
            entropy -= prob * math.log2(prob)
            
        return Ok(entropy)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "active_allocations": len(self.allocations),
            "engine": "OmniCppPracticeEngine"
        }
