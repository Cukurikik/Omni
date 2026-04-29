# Omni Resource Efficient LLM Engine
# Ref: tiingweii-shii/Awesome-Resource-Efficient-LLM-Papers
from typing import Dict
import math

def calculate_hardware_efficiency_score(params_billion: float, tokens_per_second: float, vram_gb: float) -> Dict[str, float]:
    """Calculate an abstract efficiency score for an LLM deployment."""
    if vram_gb <= 0:
        return {"efficiency_score": 0.0}
        
    # Throughput per parameter per GB VRAM
    efficiency = (tokens_per_second * params_billion) / vram_gb
    
    # Normalized against a baseline (e.g. 7B model doing 50 t/s on 16GB)
    baseline = (50.0 * 7.0) / 16.0
    normalized = min(1.0, efficiency / baseline)
    
    return {
        "raw_efficiency": round(efficiency, 4),
        "normalized_score": round(normalized, 4),
        "params_per_gb": round(params_billion / vram_gb, 4)
    }

def estimate_kv_cache_size(seq_len: int, batch_size: int, hidden_size: int, num_layers: int, precision_bytes: int = 2) -> float:
    """Estimate KV cache memory requirement in MB."""
    # 2 (K and V) * seq_len * batch_size * hidden_size * num_layers * precision
    bytes_needed = 2 * seq_len * batch_size * hidden_size * num_layers * precision_bytes
    return round(bytes_needed / (1024 * 1024), 2)
