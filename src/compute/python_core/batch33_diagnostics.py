# -*- coding: utf-8 -*-
"""
OMNI Batch 3 Semester 7 - Engine Diagnostics.

Validates that all 6 engines from Batch 3 are operational and properly
registered in the OMNI ecosystem.

Engines:
  1. OmniDRLOptimizerEngine  (AI-Optimizer)
  2. OmniColorizationEngine  (richzhang/colorization)
  3. OmniPicoGPTEngine        (picoGPT)
  4. OmniMLTutorialEngine     (ethen8181/machine-learning)
  5. OmniAdaNetEngine         (tensorflow/adanet)
  6. OmniSemanticSegEngine    (meetps/pytorch-semseg)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "system"))

from omni_drl_optimizer_engine import OmniDRLOptimizerEngine
from omni_colorization_engine import OmniColorizationEngine
from omni_pico_gpt_engine import OmniPicoGPTEngine
from omni_ml_tutorial_engine import OmniMLTutorialEngine
from omni_adanet_engine import OmniAdaNetEngine
from omni_semantic_seg_engine import OmniSemanticSegEngine


def main():
    print("=" * 70)
    print("  OMNI Semester 7 — Batch 3 — Engine Diagnostics")
    print("=" * 70)
    print()

    engines = [
        ("OmniDRLOptimizerEngine", OmniDRLOptimizerEngine),
        ("OmniColorizationEngine", OmniColorizationEngine),
        ("OmniPicoGPTEngine", OmniPicoGPTEngine),
        ("OmniMLTutorialEngine", OmniMLTutorialEngine),
        ("OmniAdaNetEngine", OmniAdaNetEngine),
        ("OmniSemanticSegEngine", OmniSemanticSegEngine),
    ]

    results = []
    all_ok = True

    for name, engine_cls in engines:
        try:
            engine = engine_cls()
            diag = engine.diagnostics()
            status = diag.get("status", "unknown")
            version = diag.get("version", "unknown")
            capabilities = diag.get("capabilities", [])

            is_ok = status == "operational"
            if not is_ok:
                all_ok = False

            icon = "OK" if is_ok else "FAIL"
            results.append((name, status, version, len(capabilities), is_ok))

            print(f"  [{icon}] {name}")
            print(f"       Status:       {status}")
            print(f"       Version:      {version}")
            print(f"       Capabilities: {len(capabilities)} methods")
            print()

        except Exception as exc:
            all_ok = False
            results.append((name, "error", "unknown", 0, False))
            print(f"  [FAIL] {name}")
            print(f"       Error: {exc}")
            print()

    print("-" * 70)
    passed = sum(1 for r in results if r[4])
    total = len(results)
    print(f"  RESULT: {passed}/{total} engines OPERATIONAL")
    if all_ok:
        print("  STATUS: ALL SYSTEMS GO")
    else:
        print("  STATUS: DEGRADED — some engines failed")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
