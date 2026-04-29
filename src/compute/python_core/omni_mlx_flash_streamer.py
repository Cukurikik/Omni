# Omni MLX Flash Weight Streamer
# Ref: matt-k-wong/mlx-flash — MIT
from typing import Dict, List

def compute_layer_schedule(total_layers: int, available_ram_gb: float,
                            layer_size_mb: float) -> Dict:
    layers_in_ram = int(available_ram_gb * 1024 / max(layer_size_mb, 0.01))
    layers_in_ram = min(layers_in_ram, total_layers)
    streamed = total_layers - layers_in_ram
    return {"in_ram": layers_in_ram, "streamed": streamed,
            "stream_ratio": round(streamed / max(total_layers, 1), 4)}

def estimate_throughput(model_size_gb: float, ram_gb: float, ssd_bandwidth_gbps: float = 5.0) -> Dict:
    if model_size_gb <= ram_gb:
        return {"mode": "full_ram", "tokens_per_sec_estimate": 50}
    stream_fraction = 1 - ram_gb / model_size_gb
    overhead_factor = 1 + stream_fraction * (model_size_gb / ssd_bandwidth_gbps)
    tps = max(1, int(50 / overhead_factor))
    return {"mode": "streaming", "tokens_per_sec_estimate": tps,
            "stream_fraction": round(stream_fraction, 4)}

def prioritize_layers(layer_freqs: List[int]) -> List[int]:
    indexed = list(enumerate(layer_freqs))
    indexed.sort(key=lambda x: x[1], reverse=True)
    return [i for i, _ in indexed]
