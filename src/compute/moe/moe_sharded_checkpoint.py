"""
moe_sharded_checkpoint.py — Compute / Storage
Layer: Compute / I/O — SafeTensors Checkpoint Sharding

MoE models are massive (e.g. Mixtral 8x7B is ~47GB). Saving them as a single
.pt file causes OOM. This module implements zero-copy sharded saving using
HuggingFace SafeTensors, saving each expert to an independent shard file.
"""
import os
import torch
import torch.nn as nn
from typing import Dict
# Note: Using torch.save as a fallback for pure zero-mock if safetensors isn't installed
try:
    from safetensors.torch import save_file, load_file
    HAS_SAFETENSORS = True
except ImportError:
    HAS_SAFETENSORS = False

class MoEShardedCheckpointer:
    def __init__(self, save_dir: str):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
    def save_moe_model(self, model: nn.Module, model_name: str):
        """
        Extracts router and experts, saving them into distinct shards.
        """
        print(f"[MoE Checkpointer] Saving sharded model to {self.save_dir}")
        
        # 1. Save router and base model weights (Shard 0)
        base_weights = {}
        expert_weights: Dict[str, Dict[str, torch.Tensor]] = {}
        
        for name, param in model.named_parameters():
            if "experts." in name:
                # Format: "layers.0.experts.4.w1.weight"
                parts = name.split("experts.")
                prefix = parts[0]
                expert_sub_name = parts[1]
                expert_id = expert_sub_name.split(".")[0]
                
                shard_name = f"{prefix}expert_{expert_id}"
                
                if shard_name not in expert_weights:
                    expert_weights[shard_name] = {}
                expert_weights[shard_name][expert_sub_name] = param.data
            else:
                base_weights[name] = param.data
                
        # Write base model
        self._write_shard(base_weights, f"{model_name}_base.safetensors")
        
        # Write experts
        for shard_name, state_dict in expert_weights.items():
            file_name = f"{model_name}_{shard_name.replace('.', '_')}.safetensors"
            self._write_shard(state_dict, file_name)
            
        print("[MoE Checkpointer] Checkpoint successfully sharded.")

    def _write_shard(self, state_dict: dict, filename: str):
        path = os.path.join(self.save_dir, filename)
        if HAS_SAFETENSORS:
            save_file(state_dict, path)
        else:
            torch.save(state_dict, path)
