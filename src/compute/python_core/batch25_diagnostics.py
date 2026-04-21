# -*- coding: utf-8 -*-
"""
Batch 25 -- Semester 3 Diagnostics Runner
Validates: WickedEngine, eqMac, SuperCollider, pyAudioAnalysis, Pedalboard
"""
import importlib
import importlib.util
import json
import os
import sys
import time

ENGINES = [
    ("omni_wicked_engine", "OmniWickedEngine"),
    ("omni_eq_mac_engine", "OmniEqMacEngine"),
    ("omni_super_collider_engine", "OmniSuperColliderEngine"),
    ("omni_py_audio_analysis_engine", "OmniPyAudioAnalysisEngine"),
    ("omni_pedalboard_engine", "OmniPedalboardEngine"),
]

def load_engine(module_name, class_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    cls = getattr(module, class_name, None)
    return cls


def main():
    print("=" * 72)
    print("  BATCH 25 -- SEMESTER 3 DIAGNOSTICS")
    print("=" * 72)

    results = []
    total_pass = 0
    total_fail = 0

    for module_name, class_name in ENGINES:
        print(f"\n  [LOAD] {class_name}...", end=" ")
        try:
            cls = load_engine(module_name, class_name)
            if cls is None:
                print("FAIL (class not found)")
                total_fail += 1
                results.append({"engine": class_name, "status": "LOAD_FAIL"})
                continue

            engine = cls()
            diag = engine.diagnostics()
            status = diag.get("status", "unknown")

            if status == "operational":
                print(f"OK -- {status.upper()}")
                total_pass += 1
            else:
                print(f"WARN -- {status}")
                total_fail += 1

            results.append({
                "engine": class_name,
                "version": diag.get("version", "?"),
                "status": status,
                "capabilities": len(diag.get("capabilities", [])),
            })

        except Exception as e:
            print(f"FAIL -- {type(e).__name__}: {e}")
            total_fail += 1
            results.append({
                "engine": class_name,
                "status": "ERROR",
                "error": f"{type(e).__name__}: {str(e)[:200]}",
            })

    print("\n" + "=" * 72)
    print(f"  RESULTS: {total_pass}/{len(ENGINES)} OPERATIONAL  | {total_fail} FAILED")
    print("=" * 72)

    for r in results:
        marker = "[OK]" if r.get("status") == "operational" else "[!!]"
        caps = r.get("capabilities", 0)
        print(f"  {marker} {r['engine']:<40} v{r.get('version', '?'):<8} caps={caps}")

    print("=" * 72)
    return total_fail == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
