import torch

# OMNI MOTHER: PiKV Paged Attention Block Allocator
# Resolves memory fragmentation in MoE context switching

class OmniPiKVAllocator:
    def __init__(self, block_size: int, num_blocks: int, device: str = 'cuda'):
        self.block_size = block_size
        self.num_blocks = num_blocks
        self.device = device
        
        # Bitmask for free blocks
        self.free_blocks = torch.ones((num_blocks,), dtype=torch.bool, device=device)
        self.block_tables = {} # Maps request_id to list of block indices

    def allocate_block(self, request_id: str) -> int:
        free_indices = torch.nonzero(self.free_blocks).squeeze(-1)
        if free_indices.numel() == 0:
            raise MemoryError("PiKV Allocator: Out of blocks")
            
        allocated_idx = free_indices[0].item()
        self.free_blocks[allocated_idx] = False
        
        if request_id not in self.block_tables:
            self.block_tables[request_id] = []
        self.block_tables[request_id].append(allocated_idx)
        
        return allocated_idx

    def free_request(self, request_id: str):
        if request_id in self.block_tables:
            for idx in self.block_tables[request_id]:
                self.free_blocks[idx] = True
            del self.block_tables[request_id]
