"""
Semester 8 Batch 23 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_ml_notes_engine import OmniMLNotesEngine
from omni_lightly_engine import OmniLightlyEngine
from omni_ai_engineering_engine import OmniAIEngineeringEngine
from omni_polyaxon_engine import OmniPolyaxonEngine
from omni_tvm_engine import OmniTVMEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 23 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniMLNotesEngine(),
        OmniLightlyEngine(),
        OmniAIEngineeringEngine(),
        OmniPolyaxonEngine(),
        OmniTVMEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 23 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
