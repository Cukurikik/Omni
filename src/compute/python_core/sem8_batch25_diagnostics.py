"""
Semester 8 Batch 25 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_stemroller_engine import OmniStemrollerEngine
from omni_imgclsmob_engine import OmniImgClsMobEngine
from omni_tensorrt_engine import OmniTensorRTEngine
from omni_mitie_engine import OmniMITIEEngine
from omni_awesome_mlss_engine import OmniAwesomeMLSSEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 25 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniStemrollerEngine(),
        OmniImgClsMobEngine(),
        OmniTensorRTEngine(),
        OmniMITIEEngine(),
        OmniAwesomeMLSSEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 25 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
