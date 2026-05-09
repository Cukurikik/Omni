import torch
import pytest
from omni_moe_grok_router import OmniMoEGrokRouter

def test_router_fairness():
    """
    OMNI Framework - PyTest Suite
    Tests the load balancing capabilities of the Grok-inspired router to ensure
    that tokens are not entirely collapsed onto a single expert (routing collapse).
    """
    batch_size = 8
    seq_len = 128
    d_model = 512
    num_experts = 8
    top_k = 2

    router = OmniMoEGrokRouter(d_model=d_model, num_experts=num_experts, top_k=top_k, jitter_eps=0.1)
    
    # Simulate a batch of random embeddings
    hidden_states = torch.randn(batch_size, seq_len, d_model)
    
    _, topk_indices, loss = router(hidden_states, training=True)
    
    # Calculate distribution
    expert_counts = torch.bincount(topk_indices.flatten(), minlength=num_experts)
    total_routing = batch_size * seq_len * top_k
    
    print(f"\nOMNI Test: Expert Distribution: {expert_counts.tolist()}")
    
    # Assert that no expert is receiving 0 tokens (given enough random samples and jitter)
    assert torch.all(expert_counts > 0), "Routing collapse detected! Some experts received 0 tokens."
    
    # Assert load balancing loss is computed correctly
    assert loss.item() > 0.0, "Load balancing loss should be strictly positive."
    
    # Check shape
    assert topk_indices.shape == (batch_size * seq_len, top_k), "TopK indices shape mismatch."
