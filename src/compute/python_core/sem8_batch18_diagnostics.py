"""
Semester 8 Batch 18 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_watermark_engine import OmniWatermarkEngine
from omni_islr_engine import OmniISLREngine
from omni_sacred_engine import OmniSacredEngine
from omni_adpapers_engine import OmniAdPapersEngine
from omni_neuro_engine import OmniNeuroEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 18 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniWatermarkEngine(),
        OmniISLREngine(),
        OmniSacredEngine(),
        OmniAdPapersEngine(),
        OmniNeuroEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 18 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
