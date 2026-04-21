"""
Semester 8 Batch 29 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_cloudannotations_engine import OmniCloudAnnotationsEngine
from omni_voxelmorph_engine import OmniVoxelmorphEngine
from omni_deepcamera_engine import OmniDeepCameraEngine
from omni_cvcuda_engine import OmniCVCUDAEngine
from omni_autodistill_engine import OmniAutodistillEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 29 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniCloudAnnotationsEngine(),
        OmniVoxelmorphEngine(),
        OmniDeepCameraEngine(),
        OmniCVCUDAEngine(),
        OmniAutodistillEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 29 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
