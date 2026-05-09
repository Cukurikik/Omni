import time
import torch

# OMNI MOTHER: LibMoE - Comprehensive Benchmarking
# Tracks FLOPs, Latency, and Memory overhead of MoE layers

class OmniLibMoEBenchmark:
    def __init__(self, model: torch.nn.Module, device: str = 'cuda'):
        self.model = model.to(device)
        self.device = device

    def measure_latency(self, input_tensor: torch.Tensor, iterations: int = 100):
        input_tensor = input_tensor.to(self.device)
        
        # Warmup
        for _ in range(10):
            with torch.no_grad():
                self.model(input_tensor)
                
        if self.device == 'cuda':
            torch.cuda.synchronize()
            
        start_time = time.time()
        for _ in range(iterations):
            with torch.no_grad():
                self.model(input_tensor)
                
        if self.device == 'cuda':
            torch.cuda.synchronize()
            
        end_time = time.time()
        avg_ms = ((end_time - start_time) / iterations) * 1000.0
        return avg_ms
