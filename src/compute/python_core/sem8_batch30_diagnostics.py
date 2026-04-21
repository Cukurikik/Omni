"""
Semester 8 Batch 30 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_hora_engine import OmniHoraEngine
from omni_openinterface_engine import OmniOpenInterfaceEngine
from omni_secretflow_engine import OmniSecretFlowEngine
from omni_awesomeai_engine import OmniAwesomeAIEngine
from omni_timellm_engine import OmniTimeLLMEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 30 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniHoraEngine(),
        OmniOpenInterfaceEngine(),
        OmniSecretFlowEngine(),
        OmniAwesomeAIEngine(),
        OmniTimeLLMEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 30 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
