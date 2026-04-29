# Omni AIMirror Download Accelerator Engine
# Ref: livehl/aimirror — MIT
from typing import List, Dict
import math

def compute_chunk_ranges(file_size: int, n_chunks: int = 8) -> List[Dict]:
    chunk_size = math.ceil(file_size / n_chunks)
    return [{"chunk_id": i, "start": i * chunk_size,
             "end": min((i+1) * chunk_size - 1, file_size - 1),
             "size": min(chunk_size, file_size - i * chunk_size)}
            for i in range(n_chunks)]

def cache_key(registry: str, package: str, version: str) -> str:
    return f"{registry}:{package}:{version}"

def should_use_cache(cache: Dict, key: str, max_age_seconds: int = 3600) -> bool:
    entry = cache.get(key)
    if not entry: return False
    return entry.get("age_seconds", max_age_seconds + 1) < max_age_seconds

def estimate_speedup(sequential_time: float, parallel_time: float) -> float:
    return round(sequential_time / max(parallel_time, 0.001), 1)

def registry_proxy_config(registries: List[str]) -> Dict:
    configs = {}
    for r in registries:
        configs[r] = {"upstream": f"https://{r}", "cache_enabled": True,
                      "parallel_chunks": 8, "max_retries": 3}
    return configs
