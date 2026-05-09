"""
moe_memory_bandwidth_calc.py — Hardware / Analysis
Layer: Compute / Analytics — MoE Hardware Profiler

Calculates theoretical Memory Bandwidth requirements and Arithmetic Intensity
for MoE models based on architecture parameters (dim, experts, batch size)
to help decide between Compute-Bound vs Memory-Bound optimization strategies.
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class MoEHardwareProfile:
    batch_size: int
    seq_len: int
    hidden_dim: int
    num_experts: int
    top_k: int
    bytes_per_param: int = 2  # FP16/BF16

class MoEBandwidthCalculator:
    """Analyzes arithmetic intensity of MoE layers."""
    
    def __init__(self, profile: MoEHardwareProfile):
        self.p = profile

    def calculate_metrics(self) -> Dict[str, float]:
        """
        Returns a dictionary of theoretical metrics for a single MoE layer.
        """
        N = self.p.batch_size * self.p.seq_len  # Total tokens
        
        # 1. Routing Cost
        # Ops: N tokens * D dim * E experts * 2 (MAC)
        routing_flops = N * self.p.hidden_dim * self.p.num_experts * 2
        
        # Memory: Load tokens (N*D), Load router weights (D*E), Store logits (N*E)
        routing_mem_bytes = (
            (N * self.p.hidden_dim) + 
            (self.p.hidden_dim * self.p.num_experts) + 
            (N * self.p.num_experts)
        ) * self.p.bytes_per_param

        # 2. Expert Compute Cost
        # Assume standard MLP: W1 (D -> 4D), W2 (4D -> D)
        # Total parameters per expert: 2 * D * 4D = 8D^2
        expert_params = 8 * (self.p.hidden_dim ** 2)
        
        # Ops: Each token goes to Top-K experts.
        # Flops per expert execution = 2 * expert_params
        expert_flops = N * self.p.top_k * (2 * expert_params)
        
        # Memory:
        # Load tokens: N * top_k * D
        # Load expert weights: In a naive implementation, all selected experts must be loaded.
        # Assuming all experts are hit at least once if N is large.
        expert_mem_bytes = (
            (N * self.p.top_k * self.p.hidden_dim) +  # Input tokens
            (self.p.num_experts * expert_params) +    # Expert weights (worst case all loaded)
            (N * self.p.top_k * self.p.hidden_dim)    # Output tokens
        ) * self.p.bytes_per_param

        # Total
        total_flops = routing_flops + expert_flops
        total_mem_bytes = routing_mem_bytes + expert_mem_bytes
        
        # Arithmetic Intensity: FLOPs / Byte
        arithmetic_intensity = total_flops / total_mem_bytes

        return {
            "total_tokens": N,
            "routing_tflops": routing_flops / 1e12,
            "routing_mem_gb": routing_mem_bytes / 1e9,
            "expert_tflops": expert_flops / 1e12,
            "expert_mem_gb": expert_mem_bytes / 1e9,
            "total_tflops": total_flops / 1e12,
            "total_mem_gb": total_mem_bytes / 1e9,
            "arithmetic_intensity_flops_per_byte": arithmetic_intensity,
            "bottleneck": "Memory-Bound" if arithmetic_intensity < 100 else "Compute-Bound" 
            # Note: 100 is a rough threshold for modern GPUs (e.g., A100 has ~312 TFLOPS / 2.0 TB/s = ~156 AI)
        }

if __name__ == "__main__":
    # Example: DeepSeek-style layer
    prof = MoEHardwareProfile(
        batch_size=32,
        seq_len=2048,
        hidden_dim=4096,
        num_experts=64,
        top_k=2
    )
    calc = MoEBandwidthCalculator(prof)
    metrics = calc.calculate_metrics()
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"{k}: {v:.2f}")
        else:
            print(f"{k}: {v}")
