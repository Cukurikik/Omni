from typing import Dict

class OmniLLM7ioRouter:
    """OMNI Compute Layer: LLM7io Gateway Router (Zero-Mock)"""
    
    def __init__(self, provider_latencies: Dict[str, float]):
        self.latencies = provider_latencies

    def select_best_provider(self, max_allowed_latency: float) -> str:
        if not self.latencies:
            raise RuntimeError("No providers configured.")
            
        valid_providers = {k: v for k, v in self.latencies.items() if v <= max_allowed_latency}
        if not valid_providers:
            raise ValueError(f"No providers available under {max_allowed_latency}ms.")
            
        return min(valid_providers, key=valid_providers.get)
