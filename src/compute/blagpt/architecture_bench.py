import time
import torch
import torch.nn as nn

def benchmark_layer(layer: nn.Module, batch_size: int, seq_len: int, dim: int, device: str = 'cuda'):
    layer = layer.to(device)
    x = torch.randn(batch_size, seq_len, dim, device=device)
    
    # Warmup
    for _ in range(10):
        _ = layer(x)
        
    torch.cuda.synchronize()
    start = time.time()
    
    for _ in range(100):
        _ = layer(x)
        
    torch.cuda.synchronize()
    end = time.time()
    
    return (end - start) / 100
