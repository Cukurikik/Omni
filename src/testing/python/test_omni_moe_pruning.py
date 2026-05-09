import pytest
import torch
import torch.nn as nn
from src.optimization.python.omni_moe_pruning import OmniMoEPruner

def test_magnitude_pruning():
    print("OMNI PyTest: Testing Magnitude Pruning Module...")
    
    # Create a dense mock expert layer
    layer = nn.Linear(10, 10)
    
    # Set known weights
    layer.weight.data = torch.arange(100, dtype=torch.float32).view(10, 10)
    
    pruner = OmniMoEPruner(layer, amount=0.5)
    pruner.apply_pruning()
    
    # 50% of the weights (the smallest 50) should be zeroed out
    zeros_count = torch.sum(layer.weight == 0).item()
    
    assert zeros_count >= 50, "Pruning did not zero out the expected number of weights."
    
    pruner.remove_pruning_reparametrization()
    
    print("OMNI PyTest: Magnitude Pruning Logic PASSED.")

# test_magnitude_pruning()
