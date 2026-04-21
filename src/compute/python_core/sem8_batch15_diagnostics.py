"""
Semester 8 Batch 15 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_djl_engine import OmniDJLEngine
from omni_spandan_dl_engine import OmniSpandanDLEngine
from omni_openmlsys_engine import OmniOpenMLSysEngine
from omni_kiln_engine import OmniKilnEngine
from omni_mlfinlab_engine import OmniMLFinLabEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 15 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniDJLEngine(),
        OmniSpandanDLEngine(),
        OmniOpenMLSysEngine(),
        OmniKilnEngine(),
        OmniMLFinLabEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 15 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
