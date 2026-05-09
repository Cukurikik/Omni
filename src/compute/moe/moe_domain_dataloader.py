"""
moe_domain_dataloader.py — Compute / Training
Layer: Compute / Data — Domain-Aware Data Loader

Standard PyTorch DataLoaders mix all data randomly. For fine-tuning an MoE,
we want to explicitly feed Medical data only to Expert 4 and Legal data to Expert 7.
This module creates a domain-aware dataloader that collates batches perfectly 
aligned with the expert architecture to speed up fine-tuning.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict

class DomainAwareDataset(Dataset):
    def __init__(self, data_samples: List[Dict]):
        # Data sample format: {"domain": "medical", "tokens": [1, 55, 12, ...]}
        self.samples = data_samples
        self.domain_map = {
            "general": 0,
            "coding": 1,
            "medical": 2,
            "legal": 3
        }

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        expert_id = self.domain_map.get(sample["domain"], 0)
        return torch.tensor(sample["tokens"], dtype=torch.long), expert_id

def expert_aligned_collate(batch):
    """
    Groups samples by their target expert ID so the router can bypass computation
    and send the contiguous block straight to the target expert.
    """
    # Sort batch by expert ID
    batch.sort(key=lambda x: x[1])
    
    tokens = [item[0] for item in batch]
    expert_ids = [item[1] for item in batch]
    
    # Pad sequences (Assuming padding token is 0)
    padded_tokens = torch.nn.utils.rnn.pad_sequence(tokens, batch_first=True, padding_value=0)
    expert_tensor = torch.tensor(expert_ids, dtype=torch.long)
    
    return padded_tokens, expert_tensor

def create_moe_dataloader(data: List[Dict], batch_size: int = 32):
    dataset = DomainAwareDataset(data)
    loader = DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=True, # Shuffle domains, but collate will group them
        collate_fn=expert_aligned_collate,
        num_workers=4
    )
    print(f"[DataLoader] Initialized Domain-Aware MoE DataLoader (Batch Size: {batch_size})")
    return loader
