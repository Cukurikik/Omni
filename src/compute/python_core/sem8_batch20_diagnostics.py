"""
Semester 8 Batch 20 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_l2l_engine import OmniL2LEngine
from omni_fincept_engine import OmniFinceptEngine
from omni_tensor_engine import OmniTensorEngine
from omni_shimmy_engine import OmniShimmyEngine
from omni_swarmui_engine import OmniSwarmUIEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 20 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniL2LEngine(),
        OmniFinceptEngine(),
        OmniTensorEngine(),
        OmniShimmyEngine(),
        OmniSwarmUIEngine(),
    ]

    healthy = 0
    for e in engines:
        try:
            diag = e.diagnostics()
            name = getattr(e, "ENGINE_ID", e.__class__.__name__)
            status = diag.get("status", "UNKNOWN")
            
            if status == "operational":
                print(f"[OK] {name} is fully operational.")
                healthy += 1
            else:
                print(f"[WARN] {name} reported non-operational status: {status}")
        except Exception as ex:
            print(f"[FAIL] {e.__class__.__name__} failed diagnostics: {ex}")

    print("\n--------------------------------------------------")
    print(f"Summary: {healthy}/{len(engines)} engines operational.")
    print("--------------------------------------------------")
    
    if healthy == len(engines):
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 20 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
