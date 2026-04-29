# Omni LLM-Drop Layer Dropping Engine
# Ref: CASE-Lab-UMD/LLM-Drop — TMLR, Apache-2.0
from typing import List, Dict
def layer_similarity(layer_a: List[float], layer_b: List[float]) -> float:
    import math
    dot = sum(a*b for a,b in zip(layer_a, layer_b))
    na = math.sqrt(sum(a**2 for a in layer_a)) or 1
    nb = math.sqrt(sum(b**2 for b in layer_b)) or 1
    return round(dot/(na*nb), 6)
def identify_redundant_layers(similarities: List[float], threshold: float = 0.95) -> List[int]:
    return [i for i, s in enumerate(similarities) if s > threshold]
def drop_layers(n_layers: int, drop_indices: List[int]) -> List[int]:
    return [i for i in range(n_layers) if i not in drop_indices]
def speedup_estimate(original_layers: int, dropped: int) -> float:
    return round(original_layers / max(original_layers - dropped, 1), 2)
