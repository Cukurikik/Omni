"""
Semester 8 Batch 28 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_mtbook_engine import OmniMTBookEngine
from omni_mars_engine import OmniMarsEngine
from omni_dalleplayground_engine import OmniDallePlaygroundEngine
from omni_pot_engine import OmniPOTEngine
from omni_unsplashdatasets_engine import OmniUnsplashDatasetsEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 28 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniMTBookEngine(),
        OmniMarsEngine(),
        OmniDallePlaygroundEngine(),
        OmniPOTEngine(),
        OmniUnsplashDatasetsEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 28 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
