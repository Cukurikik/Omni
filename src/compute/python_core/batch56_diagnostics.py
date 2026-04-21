# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_stablebaselines_engine import OmniStableBaselinesEngine
from src.compute.python_core.system.omni_ailearn_engine import OmniAiLearnEngine
from src.compute.python_core.system.omni_nsfwscraper_engine import OmniNSFWScraperEngine
from src.compute.python_core.system.omni_ludwig_engine import OmniLudwigEngine
from src.compute.python_core.system.omni_mlcourse_engine import OmniMLCourseEngine

def main():
    print("======================================================================")
    print("  BATCH 56 -- SEMESTER 7 DIAGNOSTICS (BATCH 26)")
    print("======================================================================")
    
    engines = [
        ("omni_stablebaselines_engine", OmniStableBaselinesEngine()),
        ("omni_ailearn_engine", OmniAiLearnEngine()),
        ("omni_nsfwscraper_engine", OmniNSFWScraperEngine()),
        ("omni_ludwig_engine", OmniLudwigEngine()),
        ("omni_mlcourse_engine", OmniMLCourseEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 56 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 56 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
