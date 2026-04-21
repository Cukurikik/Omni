# -*- coding: utf-8 -*-
import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_codesearchnet_engine import OmniCodeSearchNetEngine
from src.compute.python_core.system.omni_hivemind_engine import OmniHivemindEngine
from src.compute.python_core.system.omni_metarank_engine import OmniMetarankEngine
from src.compute.python_core.system.omni_synthetic_data_engine import OmniSyntheticDataEngine
from src.compute.python_core.system.omni_pytorch_kaldi_engine import OmniPyTorchKaldiEngine

def main():
    print("======================================================================")
    print("  BATCH 51 -- SEMESTER 7 DIAGNOSTICS (BATCH 21)")
    print("======================================================================")
    
    engines = [
        ("omni_codesearchnet_engine", OmniCodeSearchNetEngine()),
        ("omni_hivemind_engine", OmniHivemindEngine()),
        ("omni_metarank_engine", OmniMetarankEngine()),
        ("omni_synthetic_data_engine", OmniSyntheticDataEngine()),
        ("omni_pytorch_kaldi_engine", OmniPyTorchKaldiEngine())
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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 51 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 51 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)

if __name__ == "__main__":
    main()
