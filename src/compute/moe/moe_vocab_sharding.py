"""
moe_vocab_sharding.py — Compute / Architecture
Layer: Compute / AI — Sharded Vocabulary Embeddings

MoE models often have massive vocabularies (e.g. 128k+ tokens). An embedding matrix 
of 128k x 8192 in FP16 consumes ~2GB of VRAM just for lookups. 
This module implements Tensor Parallelism specifically for the Embedding layer, 
sharding the vocabulary across multiple GPUs to save memory.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class DistributedVocabEmbedding(nn.Module):
    """
    Shards the embedding matrix across the vocabulary dimension.
    If Vocab = 128k and World Size = 4, each GPU holds a 32k x Dim matrix.
    """
    def __init__(self, full_vocab_size: int, embedding_dim: int, world_size: int, rank: int):
        super().__init__()
        assert full_vocab_size % world_size == 0, "Vocab size must be divisible by world size."
        
        self.world_size = world_size
        self.rank = rank
        self.local_vocab_size = full_vocab_size // world_size
        
        # Calculate the range of token IDs this GPU is responsible for
        self.vocab_start_idx = rank * self.local_vocab_size
        self.vocab_end_idx = self.vocab_start_idx + self.local_vocab_size
        
        # The local shard of the embedding matrix
        self.weight = nn.Parameter(torch.empty(self.local_vocab_size, embedding_dim))
        nn.init.normal_(self.weight, mean=0.0, std=0.02)
        
        print(f"[Dist-Embed] Rank {rank}: Managing vocabulary shard [{self.vocab_start_idx} - {self.vocab_end_idx-1}].")

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        input_ids: (Batch, SeqLen) containing global token IDs.
        """
        # 1. Create a mask to identify which tokens belong to this GPU
        input_mask = (input_ids >= self.vocab_start_idx) & (input_ids < self.vocab_end_idx)
        
        # 2. Subtract offset to get local indices. Invalid tokens become 0 temporarily.
        local_ids = input_ids - self.vocab_start_idx
        local_ids = local_ids.masked_fill(~input_mask, 0)
        
        # 3. Lookup embeddings
        local_embeddings = F.embedding(local_ids, self.weight)
        
        # 4. Zero out embeddings for tokens that don't belong to this GPU
        local_embeddings = local_embeddings * input_mask.unsqueeze(-1).float()
        
        # 5. In production, we execute an All-Reduce (SUM) across all GPUs.
        # Since only one GPU has the non-zero embedding for a specific token,
        # the sum reconstructs the complete dense embedding tensor perfectly.
        # torch.distributed.all_reduce(local_embeddings, op=torch.distributed.ReduceOp.SUM)
        
        return local_embeddings
