"""
Semester 8 Batch 13 — Diagnostics
=================================
Ensures structural stability and diagnostic reporting for all
5 Batch 13 engines according to OMNI Framework bounds.
"""

from omni_ai_college_jobs_engine import OmniAICollegeJobsEngine
from omni_awesome_mlops_engine import OmniAwesomeMLOpsEngine
from omni_eagleeye_engine import OmniEagleEyeEngine
from omni_lightfm_engine import OmniLightFMEngine
from omni_marqo_engine import OmniMarqoEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 13 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniAICollegeJobsEngine(),
        OmniAwesomeMLOpsEngine(),
        OmniEagleEyeEngine(),
        OmniLightFMEngine(),
        OmniMarqoEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 13 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
