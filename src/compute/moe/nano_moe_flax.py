"""
nano_moe_flax.py — Compute / Acceleration
Layer: Compute / AI — JAX/Flax TPU MoE Layer

Inspired by Nano-MoE-JAX.
A high-performance, XLA-compilable Mixture-of-Experts layer built natively in 
JAX and Flax. Designed specifically to exploit Google TPU mesh architecture 
for massive throughput during sparse execution.
"""

import jax
import jax.numpy as jnp
import flax.linen as nn
from typing import Callable, Any

class FlaxMoELayer(nn.Module):
    """
    Replaces the standard Transformer FFN with a Sparse MoE layer in Flax.
    """
    hidden_dim: int
    num_experts: int = 8
    top_k: int = 2
    expert_dim_multiplier: int = 4
    dtype: Any = jnp.float32

    @nn.compact
    def __call__(self, x, deterministic: bool = True):
        # x shape: (batch, seq_len, hidden_dim)
        batch_size, seq_len, hidden_dim = x.shape
        flat_x = x.reshape((batch_size * seq_len, hidden_dim))
        
        # Routing Network
        gate_logits = nn.Dense(
            self.num_experts, 
            use_bias=False, 
            dtype=self.dtype,
            name="router_gate"
        )(flat_x)
        
        routing_probs = jax.nn.softmax(gate_logits, axis=-1)
        
        # Select top-k experts using jax.lax.top_k
        top_k_probs, top_k_indices = jax.lax.top_k(routing_probs, self.top_k)
        
        # Normalize probabilities across the selected experts
        top_k_probs = top_k_probs / (jnp.sum(top_k_probs, axis=-1, keepdims=True) + 1e-9)

        # For XLA compatibility, we avoid dynamic control flow.
        # We compute the output of ALL experts (since this is a Nano implementation)
        # and mask out the ones not selected. For large-scale TPU MoE, we would use 
        # jax.lax.all_gather and pmap for expert parallelism.
        
        expert_outputs = []
        for i in range(self.num_experts):
            # Define expert FFN
            e_hidden = nn.Dense(hidden_dim * self.expert_dim_multiplier, dtype=self.dtype, name=f"expert_{i}_fc1")(flat_x)
            e_hidden = nn.gelu(e_hidden)
            e_out = nn.Dense(hidden_dim, dtype=self.dtype, name=f"expert_{i}_fc2")(e_hidden)
            expert_outputs.append(e_out)
            
        # Stack all expert outputs: (batch*seq_len, num_experts, hidden_dim)
        all_expert_out = jnp.stack(expert_outputs, axis=1)
        
        # Create a mask for the selected experts
        # indices shape: (batch*seq_len, top_k)
        # We want to gather the corresponding expert outputs and multiply by weights
        
        final_output = jnp.zeros_like(flat_x)
        
        for k in range(self.top_k):
            # Extract the specific indices and weights for the k-th selected expert
            k_indices = top_k_indices[:, k]
            k_weights = top_k_probs[:, k:k+1]
            
            # Gather the expert outputs based on the indices
            selected_expert_out = jnp.take_along_axis(
                all_expert_out, 
                k_indices[:, None, None].broadcast_to((flat_x.shape[0], 1, hidden_dim)), 
                axis=1
            ).squeeze(1)
            
            # Accumulate weighted output
            final_output += selected_expert_out * k_weights

        return final_output.reshape((batch_size, seq_len, hidden_dim))
