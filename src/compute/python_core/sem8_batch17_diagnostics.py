"""
Semester 8 Batch 17 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_serenata_engine import OmniSerenataEngine
from omni_jetson_engine import OmniJetsonEngine
from omni_merlion_engine import OmniMerlionEngine
from omni_cognita_engine import OmniCognitaEngine
from omni_tfprobability_engine import OmniTFProbabilityEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 17 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniSerenataEngine(),
        OmniJetsonEngine(),
        OmniMerlionEngine(),
        OmniCognitaEngine(),
        OmniTFProbabilityEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 17 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
