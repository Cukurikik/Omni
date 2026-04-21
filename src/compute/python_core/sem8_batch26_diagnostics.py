"""
Semester 8 Batch 26 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_texthero_engine import OmniTextheroEngine
from omni_deepjazz_engine import OmniDeepjazzEngine
from omni_neuralcoref_engine import OmniNeuralcorefEngine
from omni_thinc_engine import OmniThincEngine
from omni_spiceai_engine import OmniSpiceAIEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 26 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniTextheroEngine(),
        OmniDeepjazzEngine(),
        OmniNeuralcorefEngine(),
        OmniThincEngine(),
        OmniSpiceAIEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 26 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
