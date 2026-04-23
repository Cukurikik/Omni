import datetime
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniLSMTreeCompactionEngine:
    """
    OmniLSMTreeCompactionEngine
    Batch: 27 (Semester 10)
    
    A zero-mock systems mathematical engine that calculates size-tiered 
    scaling thresholds for Log-Structured Merge-tree (LSM) architectures,
    triggering compaction events predictably.
    """
    
    def __init__(self, size_ratio: float, max_levels: int, base_level_mb: float):
        """
        :param size_ratio: The growth multiplier for each subsequent level (e.g. 10.0).
        :param max_levels: Max levels allowed before merging stops.
        :param base_level_mb: Level 0 max capacity.
        """
        self.size_ratio = size_ratio
        self.max_levels = max_levels
        self.base_level_mb = base_level_mb

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "size_ratio": self.size_ratio,
            "max_levels": self.max_levels,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def compute_level_capacities(self) -> Result[Dict[int, float], Exception]:
        """
        Calculates the max MB byte limits for all LSM levels.
        """
        try:
            if self.max_levels <= 0:
                return Err(ValueError("Max levels must be > 0"))
            if self.size_ratio <= 1.0:
                return Err(ValueError("Size ratio must be > 1.0"))
                
            capacities = {}
            for param_level in range(self.max_levels):
                cap = self.base_level_mb * (self.size_ratio ** param_level)
                capacities[param_level] = cap
                
            return Ok(capacities)
        except Exception as e:
            return Err(e)

    def evaluate_tier_health(self, current_sizes_mb: Dict[int, float]) -> Result[Dict[str, Any], Exception]:
        """
        Evaluates current tree bounds and identifies levels that require minor/major
        compaction due to capacity boundary breach.
        """
        try:
            cap_res = self.compute_level_capacities()
            if not cap_res.is_ok():
                return Err(cap_res.unwrap_err())
                
            capacities = cap_res.unwrap()
            compactions_queued = []
            
            for level, size in current_sizes_mb.items():
                if level < 0 or level >= self.max_levels:
                    # Drop blocks exceeding max levels
                    continue
                    
                max_capacity = capacities[level]
                if size >= max_capacity:
                    compactions_queued.append({
                        "level": level,
                        "current_size": size,
                        "capacity": max_capacity,
                        "overflow": size - max_capacity,
                        "target_level": min(level + 1, self.max_levels - 1)
                    })
                    
            return Ok({
                "healthy": len(compactions_queued) == 0,
                "compactions_required": len(compactions_queued),
                "queue": sorted(compactions_queued, key=lambda x: x["level"]) # higher priority L0 -> Ln
            })
        except Exception as e:
            return Err(e)
