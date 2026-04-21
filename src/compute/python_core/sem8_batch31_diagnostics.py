"""
Semester 8 Batch 31 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_trademaster_engine import OmniTradeMasterEngine
from omni_aimet_engine import OmniAIMETEngine
from omni_deepdetect_engine import OmniDeepDetectEngine
from omni_supabase_py_engine import OmniSupabasePyEngine
from omni_causalnex_engine import OmniCausalNexEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 31 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniTradeMasterEngine(),
        OmniAIMETEngine(),
        OmniDeepDetectEngine(),
        OmniSupabasePyEngine(),
        OmniCausalNexEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 31 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
