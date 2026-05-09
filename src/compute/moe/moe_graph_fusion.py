"""
moe_graph_fusion.py — Compute / Acceleration
Layer: Compute / Operations — PyTorch CUDA Graph Compilation

Executing an MoE expert requires hundreds of tiny kernel launches (e.g., small GEMMs, 
activations). The CPU overhead to queue these to the GPU is significant. 
This module captures the entire forward pass of an expert into a single static 
CUDA graph, launching all kernels with zero CPU overhead.
"""

import torch
import torch.nn as nn

class CudaGraphExpert(nn.Module):
    """
    Wraps an MoE expert module in a CUDA graph for static, zero-overhead execution.
    Requires input shapes to remain exactly identical across calls.
    """
    def __init__(self, expert_module: nn.Module, hidden_dim: int, seq_len: int = 128, batch_size: int = 1):
        super().__init__()
        self.expert = expert_module
        
        # Static memory allocations required by CUDA Graphs
        self.static_input = torch.zeros(batch_size, seq_len, hidden_dim, device='cuda')
        self.static_output = torch.zeros(batch_size, seq_len, hidden_dim, device='cuda')
        
        self.graph = None
        self._capture()
        print(f"[CUDA Graph] Successfully captured static graph for expert. CPU launch overhead eliminated.")

    def _capture(self):
        """
        Runs the warmup and captures the CUDA execution graph.
        """
        # 1. Warmup (CUDA requires a few runs to stabilize memory allocators)
        s = torch.cuda.Stream()
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            for _ in range(3):
                self.static_output = self.expert(self.static_input)
        torch.cuda.current_stream().wait_stream(s)

        # 2. Graph Capture
        self.graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.graph):
            self.static_output = self.expert(self.static_input)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Copies the input to the static memory, replays the graph, and returns the result.
        """
        if x.shape != self.static_input.shape:
            # Fallback to eager mode if the batch size or seq length differs
            return self.expert(x)

        # Copy data to the static input buffer
        self.static_input.copy_(x)
        
        # Replay the entire graph in a single GPU command
        self.graph.replay()
        
        # Return a clone of the static output so the next iteration doesn't overwrite it
        return self.static_output.clone()
