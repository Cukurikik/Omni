# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_opennmt_engine import OmniOpenNMTEngine
from src.compute.python_core.system.omni_spektral_engine import OmniSpektralEngine
from src.compute.python_core.system.omni_torchio_engine import OmniTorchIOEngine

def main():
    print("======================================================================")
    print("  BATCH 52 -- SEMESTER 7 DIAGNOSTICS (BATCH 22)")
    print("======================================================================")
    
    engines = [
        ("omni_opennmt_engine", OmniOpenNMTEngine()),
        ("omni_spektral_engine", OmniSpektralEngine()),
        ("omni_torchio_engine", OmniTorchIOEngine())
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
        print("  [OK]  ALL 3 ENGINES OPERATIONAL -- Batch 52 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 52 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
