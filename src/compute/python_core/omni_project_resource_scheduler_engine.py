from __future__ import annotations
from src.compute.python_core.omni_base_engine import Result, Ok, Err
from typing import Dict, Any, List, Set
import math

class OmniProjectResourceSchedulerEngine:
    """OMNI Zero-Prod Production Implementation for OmniProjectResourceSchedulerEngine."""
    
    def __init__(self) -> None:
        pass
        
    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniProjectResourceSchedulerEngine",
            "status": "operational",
            "batch": 53,
            "semester": 11,
            "domain": "Critical Path Method Scheduler"
        }
        
    def compute_critical_path(self, tasks: Dict[str, Dict[str, Any]]) -> Result:
        """
        Derives Critical Path Method (CPM) for natively bounding project schedules.
        Expects payload struct: { 'task_id': { 'duration': int, 'dependencies': List[str] } }
        Returns maximum schedule length natively.
        """
        try:
            if not tasks:
                return Err(ValueError("Scheduler bounds vacant"))
                
            # Compute topological sorts / native DFS bindings to prevent internal cyclical faults
            visited = set()
            temp_mark = set()
            topo_order = []
            
            def visit(node: str) -> None:
                if node in temp_mark:
                    raise ValueError(f"Cyclic dependency boundary identified recursively at {node}")
                if node not in visited:
                    temp_mark.add(node)
                    for dep in tasks.get(node, {}).get("dependencies", []):
                        if dep not in tasks:
                            raise KeyError(f"Resolution boundary fault: missing dependency {dep}")
                        visit(dep)
                    temp_mark.remove(node)
                    visited.add(node)
                    topo_order.append(node)
                    
            try:
                for t in tasks:
                    if t not in visited:
                        visit(t)
            except Exception as e:
                return Err(e)
                
            # Compute earliest completion times iteratively
            completion_times: Dict[str, float] = {}
            for t in topo_order:
                val = tasks[t]
                dur = val.get("duration", 0.0)
                if dur < 0:
                    return Err(ValueError(f"Matrix duration bounds isolated negative space on task {t}"))
                    
                deps = val.get("dependencies", [])
                max_dep_time = 0.0
                for d in deps:
                    max_dep_time = max(max_dep_time, completion_times.get(d, 0.0))
                    
                completion_times[t] = max_dep_time + dur
                
            critical_latency = max(completion_times.values(), default=0.0)
            
            return Ok({
                "critical_path_latency": round(critical_latency, 4),
                "completion_map": completion_times
            })
        except Exception as e:
            return Err(e)
