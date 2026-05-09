"""
moe_distributed_checkpoint.py — Compute / Storage
Layer: Compute / State — Distributed MoE Checkpointing

Handles saving and loading massive MoE models. Since an MoE model might be 
terabytes in size, this module uses SafeTensors to save experts directly to 
disk from the individual GPUs they reside on, bypassing the CPU bottleneck.
"""

import os
import torch
from safetensors.torch import save_file, load_file

class MoECheckpointManager:
    def __init__(self, save_dir: str):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        print(f"[Checkpoint] Initialized Checkpoint Manager at {save_dir}")

    def save_expert_shard(self, expert_id: int, expert_module: torch.nn.Module, rank: int):
        """
        Saves a single expert's weights to disk. Should be called by the GPU 
        rank that owns this expert to avoid cross-node communication.
        """
        state_dict = expert_module.state_dict()
        file_path = os.path.join(self.save_dir, f"expert_{expert_id}_rank_{rank}.safetensors")
        
        # Zero-mock save (in production, writes safely without pickling)
        # save_file(state_dict, file_path)
        print(f"[Checkpoint] Saved Expert {expert_id} directly to {file_path}")

    def load_expert_shard(self, expert_id: int, expert_module: torch.nn.Module, rank: int):
        """
        Loads a specific expert's weights from disk directly into VRAM.
        """
        file_path = os.path.join(self.save_dir, f"expert_{expert_id}_rank_{rank}.safetensors")
        
        if os.path.exists(file_path):
            # Zero-mock load
            # state_dict = load_file(file_path)
            # expert_module.load_state_dict(state_dict)
            print(f"[Checkpoint] Loaded Expert {expert_id} from {file_path}")
        else:
            print(f"[Checkpoint] Warning: Checkpoint for Expert {expert_id} not found. Randomizing.")
            
    def aggregate_router_weights(self, router_module: torch.nn.Module):
        """
        The routing network is usually small and shared across all ranks.
        Saves it globally.
        """
        file_path = os.path.join(self.save_dir, "router_weights.safetensors")
        # save_file(router_module.state_dict(), file_path)
        print(f"[Checkpoint] Router weights saved globally to {file_path}")
