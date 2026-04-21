"""
Semester 8 Batch 14 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_pytorch_forecasting_engine import OmniPyTorchForecastingEngine
from omni_argilla_engine import OmniArgillaEngine
from omni_chronos_engine import OmniChronosEngine
from omni_megengine_engine import OmniMegEngine
from omni_isr_engine import OmniISREngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 14 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniPyTorchForecastingEngine(),
        OmniArgillaEngine(),
        OmniChronosEngine(),
        OmniMegEngine(),
        OmniISREngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 14 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
