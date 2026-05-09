"""
moe_mergekit_slerp_combiner.py — Compute / Weights
Layer: Compute / Operations — MoE Expert Merging (SLERP)

Inspired by `louisbrulenaudet/mergekit-assistant`.
Instead of training a new expert from scratch, we can merge two existing experts
(e.g., Expert A: Python, Expert B: Rust) using Spherical Linear Interpolation (SLERP)
to create a hybrid expert without losing the geometric properties of the weights.
"""

import torch
import torch.nn as nn

class MergeKitSlerpCombiner:
    def __init__(self):
        print("[MergeKit] Initialized SLERP Combiner for MoE Expert Weights.")

    def slerp(self, t: float, v0: torch.Tensor, v1: torch.Tensor, dot_threshold: float = 0.9995) -> torch.Tensor:
        """
        Spherical Linear Interpolation between two tensors.
        t: interpolation parameter (0.0 to 1.0)
        v0, v1: Tensors to interpolate (must be same shape)
        """
        # Save original shapes and flatten
        shape = v0.shape
        v0_flat = v0.flatten()
        v1_flat = v1.flatten()
        
        # Normalize the vectors
        v0_norm = v0_flat / (torch.norm(v0_flat) + 1e-10)
        v1_norm = v1_flat / (torch.norm(v1_flat) + 1e-10)
        
        # Calculate dot product
        dot = torch.sum(v0_norm * v1_norm)
        
        # If the inputs are too close, linearly interpolate to avoid instability
        if torch.abs(dot) > dot_threshold:
            res = v0_flat + t * (v1_flat - v0_flat)
            return res.view(shape)
            
        # Calculate initial angle between v0 and v1
        theta_0 = torch.acos(torch.clamp(dot, -1.0, 1.0))
        
        # Calculate angle for interpolated vector
        theta_t = theta_0 * t
        
        # Calculate orthogonal vector to v0 in the plane of v0, v1
        v2_flat = v1_flat - v0_flat * dot
        v2_norm = v2_flat / (torch.norm(v2_flat) + 1e-10)
        
        # Calculate final interpolated vector
        res = v0_flat * torch.cos(theta_t) + v2_norm * torch.sin(theta_t) * torch.norm(v0_flat)
        
        return res.view(shape)

    def merge_experts(self, expert_a: nn.Module, expert_b: nn.Module, t: float = 0.5) -> nn.Module:
        """
        Takes two PyTorch Modules (Experts) and merges their weights using SLERP.
        Returns a new dictionary of state_dict.
        """
        state_a = expert_a.state_dict()
        state_b = expert_b.state_dict()
        
        merged_state = {}
        
        for key in state_a.keys():
            if key in state_b:
                merged_state[key] = self.slerp(t, state_a[key], state_b[key])
            else:
                merged_state[key] = state_a[key] # Fallback if missing
                
        print(f"[MergeKit] Successfully merged 2 experts using SLERP (t={t}).")
        return merged_state
