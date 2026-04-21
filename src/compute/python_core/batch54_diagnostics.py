# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_qdrant_engine import OmniQdrantEngine
from src.compute.python_core.system.omni_easyocr_engine import OmniEasyOCREngine
from src.compute.python_core.system.omni_xgboost_engine import OmniXGBoostEngine
from src.compute.python_core.system.omni_mlflow_engine import OmniMLflowEngine
from src.compute.python_core.system.omni_haystack_engine import OmniHaystackEngine

def main():
    print("======================================================================")
    print("  BATCH 54 -- SEMESTER 7 DIAGNOSTICS (BATCH 24)")
    print("======================================================================")
    
    engines = [
        ("omni_qdrant_engine", OmniQdrantEngine()),
        ("omni_easyocr_engine", OmniEasyOCREngine()),
        ("omni_xgboost_engine", OmniXGBoostEngine()),
        ("omni_mlflow_engine", OmniMLflowEngine()),
        ("omni_haystack_engine", OmniHaystackEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 54 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 54 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
