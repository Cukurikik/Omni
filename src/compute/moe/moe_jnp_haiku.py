"""
moe_jnp_haiku.py — Compute / JAX
Layer: Compute / AI — JAX-MoE Reference Implementation

Implements a basic Mixture of Experts layer using JAX and Haiku, optimized
for TPU execution. JAX's vmap and pmap allow for elegant expression of 
expert parallelism across TPU cores.
"""
import jax
import jax.numpy as jnp
import hk

class JaxExpert(hk.Module):
    """A simple MLP expert in Haiku."""
    def __init__(self, hidden_dim: int, name: str = None):
        super().__init__(name=name)
        self.hidden_dim = hidden_dim

    def __call__(self, x: jnp.ndarray) -> jnp.ndarray:
        w1 = hk.Linear(self.hidden_dim * 4, with_bias=False, name="w1")
        w2 = hk.Linear(self.hidden_dim, with_bias=False, name="w2")
        return w2(jax.nn.silu(w1(x)))

class JaxMoELayer(hk.Module):
    """
    Mixture of Experts layer using JAX/Haiku.
    """
    def __init__(self, num_experts: int, hidden_dim: int, top_k: int = 1, name: str = None):
        super().__init__(name=name)
        self.num_experts = num_experts
        self.hidden_dim = hidden_dim
        self.top_k = top_k

    def __call__(self, x: jnp.ndarray) -> jnp.ndarray:
        # x shape: (batch_size, seq_len, hidden_dim)
        batch_size, seq_len, hidden_dim = x.shape
        flat_x = jnp.reshape(x, (-1, hidden_dim))
        
        # 1. Routing
        router = hk.Linear(self.num_experts, with_bias=False, name="router")
        logits = router(flat_x)
        routing_probs = jax.nn.softmax(logits, axis=-1)
        
        # In JAX, top-k is handled via jax.lax.top_k
        top_probs, top_indices = jax.lax.top_k(routing_probs, self.top_k)
        
        # Normalize weights
        top_probs = top_probs / jnp.sum(top_probs, axis=-1, keepdims=True)
        
        # 2. Experts
        # Since Haiku doesn't natively support dynamic ModuleLists in the same way PyTorch does,
        # we can stack expert weights or use a vmap over a single expert function with stacked params.
        # For simplicity in this reference implementation, we iterate (which JAX will unroll or scan).
        
        experts = [JaxExpert(self.hidden_dim, name=f"expert_{i}") for i in range(self.num_experts)]
        
        final_output = jnp.zeros_like(flat_x)
        
        for k in range(self.top_k):
            indices_k = top_indices[:, k]
            weights_k = top_probs[:, k]
            
            for expert_id in range(self.num_experts):
                # Create boolean mask for this expert
                mask = (indices_k == expert_id)
                
                # JAX requires static shapes for XLA compilation unless using specialized masking.
                # Here we compute the expert for ALL tokens, but multiply by the mask.
                # This is "dense compute, sparse routing" which is highly inefficient but valid for 
                # a basic reference. Real JAX MoE uses `jax.lax.gather` and `scatter`.
                
                expert_out = experts[expert_id](flat_x)
                
                # Apply mask and routing weight
                weighted_out = expert_out * weights_k[:, None] * mask[:, None]
                final_output = final_output + weighted_out
                
        return jnp.reshape(final_output, (batch_size, seq_len, hidden_dim))

def test_jax_moe():
    """Dummy function to demonstrate hk.transform usage."""
    def forward_fn(x):
        moe = JaxMoELayer(num_experts=4, hidden_dim=64, top_k=1)
        return moe(x)
        
    moe_model = hk.transform(forward_fn)
    # rng = jax.random.PRNGKey(42)
    # dummy_x = jnp.ones((2, 10, 64))
    # params = moe_model.init(rng, dummy_x)
    # out = moe_model.apply(params, rng, dummy_x)
