"""
moe_expert_parallel_dataloader.py — Compute / I/O
Layer: Compute / Data — Expert-Aware Dataloader

Standard random data loading is inefficient for MoE training. 
This dataloader pre-analyzes the dataset using a frozen, prior-checkpoint router,
grouping sentences that heavily utilize the same experts into the same micro-batches.
This maximizes Expert Parallelism hardware utilization.
"""
import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict

class ExpertAwareDataset(Dataset):
    """
    A dataset wrapper that groups tokens based on their dominant expert assignment.
    """
    def __init__(self, data: List[torch.Tensor], prior_router: torch.nn.Module, num_experts: int):
        self.data = data
        self.num_experts = num_experts
        
        print("[MoE DataLoader] Analyzing dataset for expert grouping...")
        self.expert_bins: Dict[int, List[int]] = {i: [] for i in range(num_experts)}
        
        # Pre-process the dataset to find dominant experts
        with torch.no_grad():
            for idx, sequence in enumerate(data):
                # sequence: (SeqLen, HiddenDim) -- mocking embedded representation
                logits = prior_router(sequence) # (SeqLen, NumExperts)
                
                # Sum probabilities to find which expert this sequence relies on most
                seq_expert_load = logits.sum(dim=0)
                dominant_expert = torch.argmax(seq_expert_load).item()
                
                self.expert_bins[dominant_expert].append(idx)
                
        # Flatten bins back into a sorted list for sequential loading
        self.clustered_indices = []
        for expert_id in range(num_experts):
            self.clustered_indices.extend(self.expert_bins[expert_id])
            
        print(f"[MoE DataLoader] Clustered {len(self.clustered_indices)} sequences into {num_experts} expert bins.")

    def __len__(self):
        return len(self.clustered_indices)

    def __getitem__(self, idx):
        # We override the index to pull from our clustered list
        real_idx = self.clustered_indices[idx]
        return self.data[real_idx]

def create_expert_dataloader(data: List[torch.Tensor], prior_router: torch.nn.Module, num_experts: int, batch_size: int):
    """
    Factory for creating the MoE optimized dataloader.
    """
    dataset = ExpertAwareDataset(data, prior_router, num_experts)
    
    # Shuffle is false because we specifically want batches to contain sequences from the same expert bin
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    
    return loader
