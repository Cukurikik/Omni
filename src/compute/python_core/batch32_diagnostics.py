# -*- coding: utf-8 -*-
"""
Batch 32 Diagnostics Runner — Semester 7, Batch 2.

Validates health status for all 5 engines introduced in Semester 7 Batch 2:
  1. OmniMLWorkspaceEngine
  2. OmniRecoEngine
  3. OmniScikitLLMEngine
  4. OmniTensorWatchEngine
  5. OmniSDVEngine

Usage:
    python batch32_diagnostics.py

Expected output: All engines report OPERATIONAL status.

@since  7.0.0 (Semester 7 — Batch 2)
"""
import sys
import os

# Ensure the Omni root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.compute.python_core.system.omni_ml_workspace_engine import OmniMLWorkspaceEngine
from src.compute.python_core.system.omni_reco_engine import OmniRecoEngine
from src.compute.python_core.system.omni_scikit_llm_engine import OmniScikitLLMEngine
from src.compute.python_core.system.omni_tensorwatch_engine import OmniTensorWatchEngine
from src.compute.python_core.system.omni_sdv_engine import OmniSDVEngine


def main() -> None:
    engines = [
        ("OmniMLWorkspaceEngine", OmniMLWorkspaceEngine()),
        ("OmniRecoEngine", OmniRecoEngine()),
        ("OmniScikitLLMEngine", OmniScikitLLMEngine()),
        ("OmniTensorWatchEngine", OmniTensorWatchEngine()),
        ("OmniSDVEngine", OmniSDVEngine()),
    ]

    print("=" * 70)
    print("  OMNI Batch 32 Diagnostics — Semester 7 Batch 2")
    print("=" * 70)

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
        print("  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 32 PASSED")
    else:
        print("  [!!]  SOME ENGINES NOT OPERATIONAL -- Batch 32 FAILED")
    print("=" * 70)

    sys.exit(0 if all_operational else 1)


if __name__ == "__main__":
    main()
