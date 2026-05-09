import torch
from typing import List, Dict

class PagedKVCacheBlock:
    """
    Represents a single block in the PagedAttention memory manager.
    """
    def __init__(self, block_id: int, block_size: int, num_heads: int, head_dim: int, dtype: torch.dtype, device: torch.device):
        self.block_id = block_id
        self.block_size = block_size
        self.num_tokens = 0
        self.k_cache = torch.zeros((block_size, num_heads, head_dim), dtype=dtype, device=device)
        self.v_cache = torch.zeros((block_size, num_heads, head_dim), dtype=dtype, device=device)
        
    def append(self, keys: torch.Tensor, values: torch.Tensor) -> int:
        """Appends tokens to the block, returns number of appended tokens."""
        append_len = min(self.block_size - self.num_tokens, keys.shape[0])
        if append_len == 0:
            return 0
            
        start = self.num_tokens
        end = self.num_tokens + append_len
        self.k_cache[start:end] = keys[:append_len]
        self.v_cache[start:end] = values[:append_len]
        self.num_tokens += append_len
        return append_len

class OmniPagedAttentionManager:
    """
    vLLM-inspired PagedAttention Memory Manager for MoE decoding.
    Handles dynamic block allocation for continuous batching.
    """
    def __init__(self, num_blocks: int, block_size: int, num_heads: int, head_dim: int, device: str = "cuda:0"):
        self.block_size = block_size
        self.device = torch.device(device)
        self.free_blocks = [
            PagedKVCacheBlock(i, block_size, num_heads, head_dim, torch.float16, self.device)
            for i in range(num_blocks)
        ]
        self.sequence_block_map: Dict[str, List[PagedKVCacheBlock]] = {}

    def allocate_sequence(self, req_id: str):
        if req_id in self.sequence_block_map:
            raise ValueError(f"Sequence {req_id} already exists.")
        self.sequence_block_map[req_id] = []

    def free_sequence(self, req_id: str):
        if req_id in self.sequence_block_map:
            for block in self.sequence_block_map[req_id]:
                block.num_tokens = 0
                self.free_blocks.append(block)
            del self.sequence_block_map[req_id]

    def store_kv(self, req_id: str, keys: torch.Tensor, values: torch.Tensor):
        seq_blocks = self.sequence_block_map[req_id]
        remaining_k = keys
        remaining_v = values
        
        while remaining_k.shape[0] > 0:
            if not seq_blocks or seq_blocks[-1].num_tokens == self.block_size:
                if not self.free_blocks:
                    raise RuntimeError("OOM: No free KV cache blocks available.")
                new_block = self.free_blocks.pop(0)
                seq_blocks.append(new_block)
                
            active_block = seq_blocks[-1]
            appended = active_block.append(remaining_k, remaining_v)
            remaining_k = remaining_k[appended:]
            remaining_v = remaining_v[appended:]

    def get_kv_tensors(self, req_id: str) -> Tuple[torch.Tensor, torch.Tensor]:
        blocks = self.sequence_block_map[req_id]
        if not blocks:
            return torch.empty(0), torch.empty(0)
            
        k_list = [b.k_cache[:b.num_tokens] for b in blocks]
        v_list = [b.v_cache[:b.num_tokens] for b in blocks]
        
        return torch.cat(k_list, dim=0), torch.cat(v_list, dim=0)
