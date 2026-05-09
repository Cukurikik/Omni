import torch
import torch.nn as nn
from torch.utils.checkpoint import checkpoint

class OmniMoECheckpointedLayer(nn.Module):
    """
    OMNI Framework - MoE Activation Checkpointing
    During training/finetuning, MoE models consume massive VRAM due to activations 
    stored for backpropagation. This module wraps the MoE layer to trade compute 
    for memory by recomputing forward passes during the backward pass.
    """
    def __init__(self, moe_layer):
        super().__init__()
        self.moe_layer = moe_layer
        print("OMNI Python: Initialized Activation Checkpointing for MoE Layer.")

    def forward(self, hidden_states):
        # We define a custom forward wrapper to pass to torch.utils.checkpoint
        def custom_forward(inputs):
            return self.moe_layer(inputs)
            
        # Apply checkpointing. `use_reentrant=False` is recommended for newer PyTorch versions.
        return checkpoint(custom_forward, hidden_states, use_reentrant=False)
