"""
moe_distributed_embedding.py — Compute / Data
Layer: Compute / AI — Distributed Embedding Table

In massive MoE models, the initial embedding table (vocab_size x hidden_dim) 
can also exceed single-GPU memory. This module shards the embedding table 
across the cluster using Tensor Parallelism.
"""
import torch
import torch.nn as nn

class DistributedEmbeddingManager:
    """
    Manages a sharded embedding table across multiple GPUs using a conceptual 
    ProcessGroup (simulated here for zero-mock execution).
    """
    def __init__(self, vocab_size: int, hidden_dim: int, world_size: int, rank: int):
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.world_size = world_size
        self.rank = rank
        
        # Calculate shard size (assuming vocab_size is divisible by world_size)
        self.shard_size = vocab_size // world_size
        self.start_idx = rank * self.shard_size
        self.end_idx = self.start_idx + self.shard_size
        
        # Each GPU only holds its slice of the vocabulary
        self.embedding_shard = nn.Embedding(self.shard_size, hidden_dim)
        print(f"[MoE Embedding] GPU {rank} holding vocab range [{self.start_idx}, {self.end_idx})")

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        input_ids: (Batch, SeqLen)
        Returns the embeddings, masking out tokens that don't belong to this shard.
        """
        # Create a mask for tokens that fall into this GPU's vocab shard
        mask = (input_ids >= self.start_idx) & (input_ids < self.end_idx)
        
        # Shift indices to be 0-based for this specific embedding layer
        local_ids = input_ids - self.start_idx
        
        # Replace out-of-bounds indices with 0 to avoid CUDA memory access violations
        # (The resulting vectors will be zeroed out anyway due to the mask)
        safe_local_ids = torch.where(mask, local_ids, torch.zeros_like(local_ids))
        
        # Lookup
        local_embeddings = self.embedding_shard(safe_local_ids)
        
        # Zero out embeddings for tokens we don't own
        local_embeddings = local_embeddings * mask.unsqueeze(-1).to(local_embeddings.dtype)
        
        # In a real environment, this is followed by:
        # torch.distributed.all_reduce(local_embeddings)
        # So all GPUs get the fully populated embedding tensor
        
        return local_embeddings
