# Omni Massive Activations Detector
# Ref: locuslab/massive-activations — MIT
import math
from typing import List, Dict

def detect_massive_activations(activations: List[float], threshold_std: float = 6.0) -> Dict:
    n = len(activations)
    if n == 0: return {"n_massive": 0, "indices": [], "mean": 0, "std": 0}
    mean = sum(activations) / n
    var = sum((a - mean)**2 for a in activations) / n
    std = math.sqrt(var) if var > 0 else 1e-8
    threshold = mean + threshold_std * std
    massive = [(i, a) for i, a in enumerate(activations) if abs(a) > threshold]
    return {"n_massive": len(massive), "indices": [m[0] for m in massive],
            "max_activation": round(max(abs(a) for a in activations), 4) if activations else 0,
            "mean": round(mean, 6), "std": round(std, 6), "threshold": round(threshold, 4)}

def activation_kurtosis(activations: List[float]) -> float:
    n = len(activations)
    if n < 4: return 0
    mean = sum(activations) / n
    std = math.sqrt(sum((a - mean)**2 for a in activations) / n) or 1e-8
    kurt = sum(((a - mean) / std)**4 for a in activations) / n - 3
    return round(kurt, 4)

def layer_activation_profile(layer_stats: List[Dict]) -> Dict:
    return {"n_layers": len(layer_stats),
            "layers_with_massive": sum(1 for s in layer_stats if s.get("n_massive", 0) > 0),
            "max_activation_global": max((s.get("max_activation", 0) for s in layer_stats), default=0)}
