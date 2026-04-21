# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_caire_engine import OmniCaireEngine
from src.compute.python_core.system.omni_mitdeeplearning_engine import OmniMITDeepLearningEngine
from src.compute.python_core.system.omni_metaflow_engine import OmniMetaflowEngine
from src.compute.python_core.system.omni_sonnet_engine import OmniSonnetEngine
from src.compute.python_core.system.omni_skypilot_engine import OmniSkyPilotEngine

def main():
    print("======================================================================")
    print("  BATCH 57 -- SEMESTER 7 DIAGNOSTICS (BATCH 27)")
    print("======================================================================")
    
    engines = [
        ("omni_caire_engine", OmniCaireEngine()),
        ("omni_mitdeeplearning_engine", OmniMITDeepLearningEngine()),
        ("omni_metaflow_engine", OmniMetaflowEngine()),
        ("omni_sonnet_engine", OmniSonnetEngine()),
        ("omni_skypilot_engine", OmniSkyPilotEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 57 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 57 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
