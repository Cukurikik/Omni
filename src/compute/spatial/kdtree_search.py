import numpy as np
from typing import Any, List, Tuple

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class KDTreeGeoSearch:
    def __init__(self):
        self.points = None
        self.ids = None
        try:
            from scipy.spatial import cKDTree
            self.kdtree = None
        except ImportError:
            self.kdtree = None

    def build(self, coordinates: np.ndarray, ids: List[str]) -> OmniResult:
        """
        Builds a KD-Tree for fast spatial queries.
        Coordinates should be N x 2 array of (latitude, longitude).
        """
        if coordinates is None or len(coordinates) == 0 or len(coordinates) != len(ids):
            return OmniResult.err("Invalid coordinates or ID list")
            
        try:
            # Simple conversion to Cartesian for accurate local KD-Tree search
            # R = 6371 (Earth radius in km)
            lat = np.radians(coordinates[:, 0])
            lon = np.radians(coordinates[:, 1])
            R = 6371.0
            x = R * np.cos(lat) * np.cos(lon)
            y = R * np.cos(lat) * np.sin(lon)
            z = R * np.sin(lat)
            
            cartesian_coords = np.column_stack((x, y, z))
            
            from scipy.spatial import cKDTree
            self.kdtree = cKDTree(cartesian_coords)
            self.points = cartesian_coords
            self.ids = ids
            
            return OmniResult.ok(True)
        except Exception as e:
            return OmniResult.err(f"KD-Tree build failed: {str(e)}")

    def query_radius(self, target_lat: float, target_lon: float, radius_km: float) -> OmniResult:
        if self.kdtree is None:
            return OmniResult.err("KD-Tree not built")
            
        try:
            lat = np.radians(target_lat)
            lon = np.radians(target_lon)
            R = 6371.0
            x = R * np.cos(lat) * np.cos(lon)
            y = R * np.cos(lat) * np.sin(lon)
            z = R * np.sin(lat)
            
            target_cartesian = np.array([x, y, z])
            
            # Query KD-Tree
            indices = self.kdtree.query_ball_point(target_cartesian, r=radius_km)
            
            results = [self.ids[i] for i in indices]
            return OmniResult.ok(results)
        except Exception as e:
            return OmniResult.err(f"KD-Tree query failed: {str(e)}")
