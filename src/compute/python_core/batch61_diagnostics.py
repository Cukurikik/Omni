# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_catboost_engine import OmniCatBoostEngine
from src.compute.python_core.system.omni_imageai_engine import OmniImageAIEngine
from src.compute.python_core.system.omni_nsfwjs_engine import OmniNSFWJSEngine
from src.compute.python_core.system.omni_anylabeling_engine import OmniAnyLabelingEngine
from src.compute.python_core.system.omni_effective_tf_engine import OmniEffectiveTFEngine

def main():
    print("======================================================================")
    print("  BATCH 61 -- SEMESTER 7 DIAGNOSTICS (BATCH 31)")
    print("======================================================================")
    
    engines = [
        ("omni_catboost_engine", OmniCatBoostEngine()),
        ("omni_imageai_engine", OmniImageAIEngine()),
        ("omni_nsfwjs_engine", OmniNSFWJSEngine()),
        ("omni_anylabeling_engine", OmniAnyLabelingEngine()),
        ("omni_effective_tf_engine", OmniEffectiveTFEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 61 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 61 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
