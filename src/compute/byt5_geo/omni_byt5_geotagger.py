"""
@omni-layer Compute | @omni-source Yachay-AI/byt5-geotagging
@omni-description ByT5 geotagging engine: byte-level text encoding for
coordinate prediction with confidence-based geolocation.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniByT5Geotagger:
    def __init__(self, d=512, max_bytes=256):
        self.d = d; self.max_bytes = max_bytes
        self.byte_embeddings = [[math.sin((b+1)*(j+1)*0.01)*0.05 for j in range(d)] for b in range(256)]

    def encode_bytes(self, text: str) -> List[float]:
        raw_bytes = text.encode('utf-8')[:self.max_bytes]
        pooled = [0.0]*self.d
        for b in raw_bytes:
            for j in range(self.d):
                pooled[j] += self.byte_embeddings[b][j]
        n = max(len(raw_bytes), 1)
        return [v/n for v in pooled]

    def predict_coordinates(self, text: str) -> OmniResult:
        try:
            emb = self.encode_bytes(text)
            lat_signal = sum(emb[i] for i in range(0, self.d, 2))
            lon_signal = sum(emb[i] for i in range(1, self.d, 2))
            lat = math.tanh(lat_signal) * 90.0
            lon = math.tanh(lon_signal) * 180.0
            confidence = 1.0 / (1.0 + math.exp(-abs(lat_signal + lon_signal)))
            return OmniResult(data={"latitude": lat, "longitude": lon, "confidence": confidence, "byte_length": len(text.encode('utf-8')[:self.max_bytes])})
        except Exception as e: return OmniResult(error=e)

    def batch_predict(self, texts: List[str]) -> OmniResult:
        try:
            results = []
            for text in texts:
                r = self.predict_coordinates(text)
                if r.is_ok(): results.append(r.data)
            avg_conf = sum(r["confidence"] for r in results) / max(len(results), 1)
            return OmniResult(data={"predictions": results, "n_texts": len(texts), "avg_confidence": avg_conf})
        except Exception as e: return OmniResult(error=e)

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1); dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
