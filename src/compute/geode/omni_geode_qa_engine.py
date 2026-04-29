from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI Geode QA Engine — Compute Layer
# Absorbing devashish-gupta/Geode: Zero-shot geospatial question answering with explicit reasoning.

@dataclass
class GeodeResult:
    ok: bool
    answer_coords: tuple = None
    reasoning_chain: list = None
    error: str = None

class OmniGeodeQaEngine:
    def __init__(self):
        self.queries = 0
        self.spatial_index = {}

    def register_location(self, name: str, lat: float, lon: float, attributes: Dict[str, Any] = None):
        self.spatial_index[name.lower()] = {"lat": lat, "lon": lon, "attrs": attributes or {}}

    def haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        import math
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def spatial_query(self, query_lat: float, query_lon: float, radius_km: float) -> GeodeResult:
        if not self.spatial_index:
            return GeodeResult(False, error="GeodeError: Spatial index empty")
        self.queries += 1
        reasoning = []
        matches = []
        for name, loc in self.spatial_index.items():
            dist = self.haversine_km(query_lat, query_lon, loc["lat"], loc["lon"])
            reasoning.append(f"Distance to '{name}': {dist:.2f} km")
            if dist <= radius_km:
                matches.append((name, loc["lat"], loc["lon"], dist))
        matches.sort(key=lambda x: x[3])
        if not matches:
            return GeodeResult(False, reasoning_chain=reasoning, error="GeodeError: No locations within radius")
        best = matches[0]
        return GeodeResult(True, answer_coords=(best[1], best[2]), reasoning_chain=reasoning)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniGeodeQaEngine", "indexed_locations": len(self.spatial_index),
                "queries": self.queries, "status": "Operational"}
