# Omni RS-SpatioTemporal VLM Engine
# Ref: Chen-Yang-Liu/Awesome-RS-SpatioTemporal-VLMs
from typing import List, Dict

def spatial_change_detection(t1_features: List[float], t2_features: List[float],
                              threshold: float = 0.3) -> Dict:
    diff = [abs(a - b) for a, b in zip(t1_features, t2_features)]
    changed = sum(1 for d in diff if d > threshold)
    return {"change_ratio": round(changed / max(len(diff), 1), 4),
            "max_change": round(max(diff) if diff else 0, 4),
            "mean_change": round(sum(diff) / max(len(diff), 1), 4)}

def temporal_embedding(timestamps: List[float], dim: int = 32) -> List[List[float]]:
    import math
    return [[round(math.sin(t * (i+1) * 0.01) + math.cos(t * (i+1) * 0.007), 6)
             for i in range(dim)] for t in timestamps]

def caption_geo_features(bands: Dict[str, float]) -> str:
    parts = []
    ndvi = (bands.get("NIR", 0) - bands.get("RED", 0)) / max(bands.get("NIR", 0) + bands.get("RED", 0), 1e-6)
    if ndvi > 0.3: parts.append("vegetation present")
    elif ndvi < 0: parts.append("water body detected")
    else: parts.append("bare soil or urban area")
    return "; ".join(parts) if parts else "unclassified"
