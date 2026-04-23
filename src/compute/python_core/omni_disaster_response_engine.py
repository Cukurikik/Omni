"""OmniDisasterResponseEngine - Euclidean spatial triage and resource distribution optimization."""
import math
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniDisasterResponseEngine:
    """OMNI Production Engine: OmniDisasterResponseEngine. Zero-Prod compliant."""
    def __init__(self):
        self.version = "3.7.0"
        
    def optimize_resource_distribution(self, incidents, resources):
        """Perform optimize resource distribution computation.

            Args:
                    incidents
                    resources

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not isinstance(incidents, list) or not isinstance(resources, list):
            return {"status": "error", "error": "Inputs must be explicitly defined arrays of coordinate topologies."}
            
        allocations = []
        unassigned_incidents = set(range(len(incidents)))
        available_resources = set(range(len(resources)))
        
        # We perform an exact O(N^2) greedy spatial proximity calculation
        # In a real disaster system, this serves as the foundational geometric solver
        
        matches_found = 0
        total_distance_covered = 0.0
        
        for inc_idx in sorted(unassigned_incidents):
            inc = incidents[inc_idx]
            min_dist = float('inf')
            best_res = -1
            
            for res_idx in sorted(available_resources):
                res = resources[res_idx]
                
                # Euclidean distance bounding
                dx = inc.get("x", 0) - res.get("x", 0)
                dy = inc.get("y", 0) - res.get("y", 0)
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Enforce strict priority triage metrics, if incident has 'severity', adjust effective distance
                severity_factor = max(1.0, inc.get("severity", 1.0))
                effective_dist = dist / severity_factor
                
                if effective_dist < min_dist:
                    min_dist = effective_dist
                    best_res = res_idx
                    actual_dist = dist
                    
            if best_res != -1:
                allocations.append({
                    "incident_id": inc_idx,
                    "resource_id": best_res,
                    "spatial_distance": round(actual_dist, 4)
                })
                available_resources.remove(best_res)
                matches_found += 1
                total_distance_covered += actual_dist
                
                
        return {
            "status": "ok",
            "value": {
                "allocations_completed": matches_found,
                "unresolved_incidents": len(incidents) - matches_found,
                "unused_resources": len(available_resources),
                "total_spatial_distribution_cost": round(total_distance_covered, 4),
                "mapping": allocations
            }
        }

    def diagnostics(self):
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "version": self.version
        }
