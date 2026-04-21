"""
Semester 8 Batch 21 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_fsrs_engine import OmniFSRSEngine
from omni_satellite_datasets_engine import OmniSatelliteDatasetsEngine
from omni_arxiv_times_engine import OmniArXivTimesEngine
from omni_gophernotes_engine import OmniGopherNotesEngine
from omni_teachable_machine_engine import OmniTeachableMachineEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 21 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniFSRSEngine(),
        OmniSatelliteDatasetsEngine(),
        OmniArXivTimesEngine(),
        OmniGopherNotesEngine(),
        OmniTeachableMachineEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 21 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
