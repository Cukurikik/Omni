# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_fastbook_engine import OmniFastbookEngine
from src.compute.python_core.system.omni_paddle_engine import OmniPaddleEngine
from src.compute.python_core.system.omni_homemademl_engine import OmniHomemadeMLEngine
from src.compute.python_core.system.omni_chatterbot_engine import OmniChatterBotEngine
from src.compute.python_core.system.omni_nni_engine import OmniNNIEngine

def main():
    print("======================================================================")
    print("  BATCH 55 -- SEMESTER 7 DIAGNOSTICS (BATCH 25)")
    print("======================================================================")
    
    engines = [
        ("omni_fastbook_engine", OmniFastbookEngine()),
        ("omni_paddle_engine", OmniPaddleEngine()),
        ("omni_homemademl_engine", OmniHomemadeMLEngine()),
        ("omni_chatterbot_engine", OmniChatterBotEngine()),
        ("omni_nni_engine", OmniNNIEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 55 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 55 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
