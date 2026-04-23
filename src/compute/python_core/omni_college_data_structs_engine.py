from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniCollegeDataStructsEngine(OmniBaseEngine):
    """
    Implements advanced algorithmic simulations for standard C-like
    data structures, notably a deterministic contiguous memory pool allocator.
    """
    
    def __init__(self, pool_capacity: int):
        super().__init__()
        self.pool_capacity = pool_capacity
        self.allocated_blocks: List[Dict[str, int]] = []

    def allocate(self, size: int, alignment: int = 8) -> Result[Dict[str, int], str]:
        """
        Allocates a block of memory deterministically searching for the
        first fit free space inside the structured linear bound.
        """
        if size <= 0:
            return Result.fail("Allocation size must be positive.")
            
        req_size = size + (alignment - (size % alignment)) if (size % alignment) != 0 else size
        
        if not self.allocated_blocks:
            if req_size <= self.pool_capacity:
                block = {"offset": 0, "size": req_size}
                self.allocated_blocks.append(block)
                return Result.ok(block)
            return Result.fail("Initial allocation exceeds contiguous pool limit.")
                
        # Sorted by offset
        self.allocated_blocks.sort(key=lambda b: b["offset"])
        
        current_offset = 0
        for block in self.allocated_blocks:
            gap = block["offset"] - current_offset
            if gap >= req_size:
                new_block = {"offset": current_offset, "size": req_size}
                self.allocated_blocks.append(new_block)
                self.allocated_blocks.sort(key=lambda b: b["offset"])
                return Result.ok(new_block)
            current_offset = block["offset"] + block["size"]
            
        # Check end gap
        gap = self.pool_capacity - current_offset
        if gap >= req_size:
            new_block = {"offset": current_offset, "size": req_size}
            self.allocated_blocks.append(new_block)
            self.allocated_blocks.sort(key=lambda b: b["offset"])
            return Result.ok(new_block)
            
        return Result.fail("Memory allocator bounds overflow: Heap corruption protected.")

    def deallocate(self, offset: int) -> Result[bool, str]:
        """
        Frees a previously allocated structured block.
        """
        for i, block in enumerate(self.allocated_blocks):
            if block["offset"] == offset:
                del self.allocated_blocks[i]
                return Result.ok(True)
        return Result.fail(f"Invalid allocation offset: {offset} not mapped.")

    def get_fragmentation_metric(self) -> Result[float, str]:
        """
        Computes the ratio of gap spaces to valid allocated clusters.
        """
        if not self.allocated_blocks:
            return Result.ok(0.0)
            
        self.allocated_blocks.sort(key=lambda b: b["offset"])
        gaps = 0.0
        curr = 0
        for block in self.allocated_blocks:
            if block["offset"] > curr:
                gaps += float(block["offset"] - curr)
            curr = block["offset"] + block["size"]
        
        if curr < self.pool_capacity:
            gaps += float(self.pool_capacity - curr)
            
        return Result.ok(gaps / float(self.pool_capacity))

    def compute_memory_alignment_offset(self, memory_address: int, alignment_boundary: int) -> Result[int, str]:
        """Perform compute memory alignment offset computation.

            Args:
                    memory_address: int
                    alignment_boundary: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if alignment_boundary <= 0 or (alignment_boundary & (alignment_boundary - 1)) != 0:
            return Result.fail("Alignment boundary must be a power of 2 greater than 0")
        offset = memory_address % alignment_boundary
        padding = (alignment_boundary - offset) if offset != 0 else 0
        return Result.ok(memory_address + padding)

    def diagnostics(self) -> dict:
        """Return engine diagnostic metadata.

        Returns:
            dict: Engine name, version, and operational status.
        """
        return {"engine": "OmniCollegeDataStructsEngine", "version": "1.0.0", "status": "operational"}
