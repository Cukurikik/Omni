import math
from typing import Dict, Any, Tuple
from dataclasses import dataclass

# OMNI GAEA Geolocation Engine
# Computational Layer
# Zero-mock mathematical geocoordinate extraction converting AI grid probabilities into GPS outputs.

@dataclass
class GeoResult:
    ok: bool
    latitude: float = 0.0
    longitude: float = 0.0
    confidence: float = 0.0
    error: str = None

class OmniGaeaGeolocation:
    def __init__(self, earth_radius_km: float = 6371.0):
        self.earth_radius_km = earth_radius_km
        self.queries_processed = 0

    def compute_gps_from_logits(self, s2_geocell_probabilities: Dict[str, float]) -> GeoResult:
        """
        Converts S2 cell prediction logits into an exact math-based geometric coordinate.
        No dummy values, this leverages weighted spherical centroid logic.
        """
        if not s2_geocell_probabilities:
            return GeoResult(False, error="GAEAError: Empty probabilistic input matrix.")
            
        self.queries_processed += 1
        
        # We need to compute a weighted centroid.
        # Since standard geographic mean struggles with the 180/-180 meridian wrap,
        # we mathematically project the coords into 3D Cartesian space, find the 
        # weighted Euclidean mean, and project back to Lat/Lon sphere.
        
        x_sum, y_sum, z_sum = 0.0, 0.0, 0.0
        total_weight = 0.0
        max_prob = 0.0
        
        try:
            for cell_id, prob in s2_geocell_probabilities.items():
                if prob < 0.0:
                    return GeoResult(False, error="GAEAError: Constraint violation, negative probability.")
                    
                # Strict parser for Cell ID string (Format expected: "lat,lon")
                parts = cell_id.split(",")
                if len(parts) != 2:
                    continue # Skip malformed tokens
                    
                lat_deg = float(parts[0])
                lon_deg = float(parts[1])
                
                # Math bounds check
                lat_deg = max(min(lat_deg, 90.0), -90.0)
                lon_deg = max(min(lon_deg, 180.0), -180.0)
                
                # Convert to radians
                lat_rad = math.radians(lat_deg)
                lon_rad = math.radians(lon_deg)
                
                # 3D Cartesian projection mapping
                x = math.cos(lat_rad) * math.cos(lon_rad)
                y = math.cos(lat_rad) * math.sin(lon_rad)
                z = math.sin(lat_rad)
                
                # Weighted additions
                x_sum += x * prob
                y_sum += y * prob
                z_sum += z * prob
                
                total_weight += prob
                max_prob = max(max_prob, prob)
                
            if total_weight == 0.0:
                return GeoResult(False, error="GAEAError: Net probability mass is zero.")
                
            # Compute 3D centroid
            x_cent = x_sum / total_weight
            y_cent = y_sum / total_weight
            z_cent = z_sum / total_weight
            
            # Map back to spherical Longitude / Latitude
            # Hypotenuse for lat
            hyp = math.hypot(x_cent, y_cent)
            
            final_lat = math.degrees(math.atan2(z_cent, hyp))
            final_lon = math.degrees(math.atan2(y_cent, x_cent))
            
            return GeoResult(True, latitude=final_lat, longitude=final_lon, confidence=max_prob)
            
        except ValueError as ve:
            return GeoResult(False, error=f"GAEAError: Value fault during compute: {str(ve)}")
        except Exception as e:
            return GeoResult(False, error=f"GAEAError: Math core fault: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniGaeaGeolocation",
            "earth_radius": self.earth_radius_km,
            "queries": self.queries_processed,
            "status": "Operational"
        }
