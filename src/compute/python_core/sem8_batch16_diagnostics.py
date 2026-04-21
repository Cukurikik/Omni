"""
Semester 8 Batch 16 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_rath_engine import OmniRathEngine
from omni_sd_videos_engine import OmniSDVideosEngine
from omni_econml_engine import OmniEconMLEngine
from omni_tf_datasets_engine import OmniTFDatasetsEngine
from omni_accordnet_engine import OmniAccordNetEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 16 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniRathEngine(),
        OmniSDVideosEngine(),
        OmniEconMLEngine(),
        OmniTFDatasetsEngine(),
        OmniAccordNetEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 16 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
