# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_cleanrl_engine import OmniCleanRLEngine
from src.compute.python_core.system.omni_oneflow_engine import OmniOneFlowEngine
from src.compute.python_core.system.omni_flexllmgen_engine import OmniFlexLLMGenEngine
from src.compute.python_core.system.omni_darts_engine import OmniDartsEngine
from src.compute.python_core.system.omni_roboflow_engine import OmniRoboflowEngine

def main():
    print("======================================================================")
    print("  BATCH 59 -- SEMESTER 7 DIAGNOSTICS (BATCH 29)")
    print("======================================================================")
    
    engines = [
        ("omni_cleanrl_engine", OmniCleanRLEngine()),
        ("omni_oneflow_engine", OmniOneFlowEngine()),
        ("omni_flexllmgen_engine", OmniFlexLLMGenEngine()),
        ("omni_darts_engine", OmniDartsEngine()),
        ("omni_roboflow_engine", OmniRoboflowEngine())
    ]
    
    all_operational = True
    for name, engine in engines:
        diag = engine.diagnostics()
        status = diag.get("status", "UNKNOWN").upper()
        caps = diag.get("capabilities", [])
        version = diag.get("version", "?")

        icon = "[OK]" if status == "OPERATIONAL" else "[!!]"
        print(f"\n{icon}  {name} v{version}")
        print(f"     Status       : {status}")
        print(f"     Capabilities : {len(caps)}")
        for cap in caps:
            print(f"       - {cap}")

        if status != "OPERATIONAL":
            all_operational = False

    print("\n" + "=" * 70)
    if all_operational:
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 59 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 59 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
