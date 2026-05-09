"""
moe_residual_inspector.py — Compute / Observability
Layer: Compute / AI — Internal Transformer Inspector

Inspired by Noesis.
A lightweight toolkit designed to inspect the internals of the MoE model during 
the forward pass. It calculates the drift in the residual stream and the 
activation delta added by the MoE layer to detect "expert collapse" or 
"representation drift".
"""

import torch
import torch.nn as nn

class ResidualInspector:
    """
    Hooks into the transformer blocks to measure how much the MoE layer
    actually alters the token representations.
    """
    def __init__(self):
        self.layer_drifts = {}
        print("[Noesis Inspector] Transformer residual tracking initialized.")

    def compute_cosine_drift(self, pre_residual: torch.Tensor, post_residual: torch.Tensor) -> float:
        """
        Calculates the average cosine similarity between the stream before 
        and after the MoE application. A similarity near 1.0 means the MoE did nothing.
        """
        # Flatten sequence length for token-wise comparison
        pre = pre_residual.view(-1, pre_residual.size(-1))
        post = post_residual.view(-1, post_residual.size(-1))
        
        sims = torch.nn.functional.cosine_similarity(pre, post, dim=-1)
        return sims.mean().item()

    def compute_activation_magnitude(self, moe_delta: torch.Tensor) -> float:
        """
        Calculates the L2 norm of the delta injected by the experts.
        """
        return torch.norm(moe_delta, p=2, dim=-1).mean().item()

    def inspect_layer(self, layer_idx: int, pre_res: torch.Tensor, moe_out: torch.Tensor, post_res: torch.Tensor):
        """
        Logs the inspection metrics for a specific layer.
        """
        drift = self.compute_cosine_drift(pre_res, post_res)
        magnitude = self.compute_activation_magnitude(moe_out)
        
        self.layer_drifts[layer_idx] = {
            "cosine_similarity": drift,
            "moe_injection_norm": magnitude
        }
        
        # Warn if the MoE is effectively dead
        if drift > 0.999 and magnitude < 1e-4:
            print(f"[Noesis Alert] Layer {layer_idx} MoE is inactive! (Sim: {drift:.4f}, Norm: {magnitude:.4f})")

# Typical usage inside the Transformer Loop:
# pre_res = hidden_states.clone()
# moe_out = moe_layer(hidden_states)
# hidden_states = hidden_states + moe_out
# inspector.inspect_layer(layer_id, pre_res, moe_out, hidden_states)
