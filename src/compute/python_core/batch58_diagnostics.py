# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_computervisionrecipes_engine import OmniComputerVisionRecipesEngine
from src.compute.python_core.system.omni_pyod_engine import OmniPyODEngine
from src.compute.python_core.system.omni_pycaret_engine import OmniPyCaretEngine
from src.compute.python_core.system.omni_sktime_engine import OmniSktimeEngine
from src.compute.python_core.system.omni_gorse_engine import OmniGorseEngine

def main():
    print("======================================================================")
    print("  BATCH 58 -- SEMESTER 7 DIAGNOSTICS (BATCH 28)")
    print("======================================================================")
    
    engines = [
        ("omni_computervisionrecipes_engine", OmniComputerVisionRecipesEngine()),
        ("omni_pyod_engine", OmniPyODEngine()),
        ("omni_pycaret_engine", OmniPyCaretEngine()),
        ("omni_sktime_engine", OmniSktimeEngine()),
        ("omni_gorse_engine", OmniGorseEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 58 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 58 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
