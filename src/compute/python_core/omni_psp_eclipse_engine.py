from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniPspEclipseEngine(OmniBaseEngine):
    """
    Evaluates Personal Software Process matrices mapping chronological time injections
    and discrete deterministic bug resolutions establishing density indexes.
    """
    
    def __init__(self):
        super().__init__()
        self.phases = ["PLAN", "DESIGN", "CODE", "COMPILE", "TEST", "P-MORTEM"]
        self.logs: List[Dict[str, Any]] = []

    def log_time_entry(self, phase: str, delta_minutes: int) -> Result[bool, str]:
        """
        Structures a chronological mapping bounding vector logs.
        """
        if phase not in self.phases:
            return Result.fail("Invalid bounding topology mapping phase.")
            
        if delta_minutes < 0:
            return Result.fail("Temporal disruption: Log must be scalar positive.")
            
        self.logs.append({"type": "TIME", "phase": phase, "val": delta_minutes})
        return Result.ok(True)

    def log_defect(self, phase_injected: str, phase_removed: str, fix_time: int) -> Result[bool, str]:
        """Perform log defect computation.

            Args:
                    phase_injected: str
                    phase_removed: str
                    fix_time: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if phase_injected not in self.phases or phase_removed not in self.phases:
            return Result.fail("Invalid domain state for topological node constraints.")
            
        idx_in = self.phases.index(phase_injected)
        idx_out = self.phases.index(phase_removed)
        
        if idx_out < idx_in:
            return Result.fail("Temporal paradox: Defect removed prior to geometric injection.")
            
        self.logs.append({
            "type": "DEFECT", 
            "injected": phase_injected, 
            "removed": phase_removed, 
            "time": fix_time
        })
        return Result.ok(True)

    def compute_yield_metrics(self) -> Result[Dict[str, float], str]:
        """
        Derives an absolute Phase Yield index via strict O(N) traversal.
        """
        if not self.logs:
            return Result.ok({"total_time": 0.0, "defect_density": 0.0})
            
        total_t = 0
        total_defects = 0
        pre_compile_inj = 0
        pre_compile_rem = 0
        
        for l in self.logs:
            if l["type"] == "TIME":
                total_t += l["val"]
            elif l["type"] == "DEFECT":
                total_defects += 1
                total_t += l["time"]
                
                idx_in = self.phases.index(l["injected"])
                idx_rm = self.phases.index(l["removed"])
                
                if idx_in < 3: # Before compile
                    pre_compile_inj += 1
                if idx_rm < 3:
                    pre_compile_rem += 1
                    
        volumetrics = 0.0
        if pre_compile_inj > 0:
            volumetrics = float(pre_compile_rem) / float(pre_compile_inj)
            
        return Result.ok({
            "total_time": float(total_t),
            "defect_density": float(total_defects) / max(1.0, float(total_t) / 60.0),
            "phase_yield": volumetrics
        })

    def measure_personal_defect_density(self, defect_count: int, loc: int) -> Result[float, str]:
        """Perform measure personal defect density computation.

            Args:
                    defect_count: int
                    loc: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if loc <= 0 or defect_count < 0: return Result.fail("Invalid metrics")
        return Result.ok((defect_count / loc) * 1000)

    def diagnostics(self) -> dict:
        """Return engine diagnostic metadata.

        Returns:
            dict: Engine name, version, and operational status.
        """
        return {"engine": "OmniPspEclipseEngine", "version": "1.0.0", "status": "operational"}
