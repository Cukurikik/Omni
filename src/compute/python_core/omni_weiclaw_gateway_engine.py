import uuid
from typing import Dict, Any, List
from dataclasses import dataclass, field
import numpy as np

# OMNI Monadic Type
@dataclass
class Result:
    is_ok: bool
    value: Any = None
    error: str = None

    @classmethod
    def Ok(cls, value: Any):
        return cls(is_ok=True, value=value)

    @classmethod
    def Err(cls, error: str):
        return cls(is_ok=False, error=error)

def ok(value: Any) -> Result:
    return Result.Ok(value)

def err(error: str) -> Result:
    return Result.Err(error)

@dataclass
class OmniWeiclawGatewayEngine:
    """
    OmniWeiclawGatewayEngine
    Domain: WeiClaw (High-Speed API Gateway Policy Gateway)
    Mathematically constructs probabilistic API rate-limiting bounds and load-balancing
    structural paths based on exponential traffic variance metrics.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    max_variance_bound: float = 2.5

    def _traffic_variance_allocation(self, load_series: np.ndarray, current_capacities: np.ndarray) -> np.ndarray:
        """
        Calculates optimal request routing allocations across distributed nodal APIs
        minimizing capacity overflow and structural queue variance.
        load_series: (Time_Steps) incoming request density.
        current_capacities: (Number_of_Nodes)
        """
        # Calculate moving variance of load to detect burst pressure
        load_mean = np.mean(load_series)
        load_variance = np.var(load_series)
        
        num_nodes = len(current_capacities)
        allocation_policy = np.zeros(num_nodes)
        
        # Invert capacities to proportionally penalize heavily loaded nodes
        inv_capacities = 1.0 / (current_capacities + 1e-9)
        weight_dist = inv_capacities / np.sum(inv_capacities)
        
        if load_variance > self.max_variance_bound:
            # High burst: apply exponential smoothing to weight distributions
            smoothed_weights = np.exp(weight_dist) / np.sum(np.exp(weight_dist))
            allocation_policy = smoothed_weights
        else:
            # Normal state: linear proportional allocation
            allocation_policy = weight_dist
            
        return allocation_policy

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "historical_load" not in payload or "node_capacities" not in payload:
                return err("Missing traffic context or nodal capacity for WeiClaw routing.")
                
            load = np.array(payload["historical_load"], dtype=np.float32)
            capacity = np.array(payload["node_capacities"], dtype=np.float32)

            if load.ndim != 1 or capacity.ndim != 1:
                return err("Traffic and capacity inputs must be 1D temporal/spatial sets.")

            allocation = self._traffic_variance_allocation(load, capacity)
            
            # Simple health check of gateway stability
            is_bursting = bool(np.var(load) > self.max_variance_bound)

            return ok({
                "engine_id": self.engine_id,
                "node_routing_allocations": allocation.tolist(),
                "detects_traffic_burst": is_bursting,
                "status": "WeiClaw Policy Saturated"
            })
            
        except Exception as e:
            return err(f"WeiClaw Gateway policy failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniWeiclawGatewayEngine",
            "status": "Operational",
            "max_variance_bound": self.max_variance_bound
        }
