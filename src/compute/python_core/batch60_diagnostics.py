# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_autokeras_engine import OmniAutoKerasEngine
from src.compute.python_core.system.omni_rvm_engine import OmniRVMEngine
from src.compute.python_core.system.omni_project_ideas_engine import OmniProjectIdeasEngine
from src.compute.python_core.system.omni_pyro_engine import OmniPyroEngine
from src.compute.python_core.system.omni_cnn_explainer_engine import OmniCNNExplainerEngine

def main():
    print("======================================================================")
    print("  BATCH 60 -- SEMESTER 7 DIAGNOSTICS (BATCH 30)")
    print("======================================================================")
    
    engines = [
        ("omni_autokeras_engine", OmniAutoKerasEngine()),
        ("omni_rvm_engine", OmniRVMEngine()),
        ("omni_project_ideas_engine", OmniProjectIdeasEngine()),
        ("omni_pyro_engine", OmniPyroEngine()),
        ("omni_cnn_explainer_engine", OmniCNNExplainerEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 60 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 60 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
