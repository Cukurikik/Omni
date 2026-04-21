# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_photoprism_engine import OmniPhotoPrismEngine
from src.compute.python_core.system.omni_paperlessngx_engine import OmniPaperlessNGXEngine
from src.compute.python_core.system.omni_supervision_engine import OmniSupervisionEngine
from src.compute.python_core.system.omni_vane_engine import OmniVaneEngine
from src.compute.python_core.system.omni_aiengineeringhub_engine import OmniAIEngineeringHubEngine

def main():
    print("======================================================================")
    print("  BATCH 53 -- SEMESTER 7 DIAGNOSTICS (BATCH 23)")
    print("======================================================================")
    
    engines = [
        ("omni_photoprism_engine", OmniPhotoPrismEngine()),
        ("omni_paperlessngx_engine", OmniPaperlessNGXEngine()),
        ("omni_supervision_engine", OmniSupervisionEngine()),
        ("omni_vane_engine", OmniVaneEngine()),
        ("omni_aiengineeringhub_engine", OmniAIEngineeringHubEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 53 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 53 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
