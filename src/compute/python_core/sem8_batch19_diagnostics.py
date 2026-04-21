"""
Semester 8 Batch 19 — Diagnostics
=================================
Diagnostics checking for zero-mock implementations.
"""

from omni_algowiki_engine import OmniAlgoWikiEngine
from omni_cml_engine import OmniCMLEngine
from omni_bindu_engine import OmniBinduEngine
from omni_brag_engine import OmniBRAGEngine
from omni_llmrl_engine import OmniLLMRLEngine

def run_diagnostics():
    print("--------------------------------------------------")
    print("OMNI SEMESTER 8 BATCH 19 DIAGNOSTICS")
    print("--------------------------------------------------\n")

    engines = [
        OmniAlgoWikiEngine(),
        OmniCMLEngine(),
        OmniBinduEngine(),
        OmniBRAGEngine(),
        OmniLLMRLEngine(),
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
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 19 IS LIVE.")
        return 0
    else:
        print("SYSTEM DEGRADATION DETECTED.")
        return 1

if __name__ == "__main__":
    exit(run_diagnostics())
