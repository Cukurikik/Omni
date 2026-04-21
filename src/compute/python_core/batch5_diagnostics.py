# -*- coding: utf-8 -*-
"""
Batch 5 (Semester 7) — Diagnostic Runner
Validates all 5 Batch 5 engines are importable and operational.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def run_batch5_diagnostics():
    engines = [
        ("system.omni_pennylane_qml_engine", "OmniPennyLaneQMLEngine"),
        ("system.omni_damo_yolo_engine", "OmniDamoYoloEngine"),
        ("system.omni_fastnlp_engine", "OmniFastNLPEngine"),
        ("system.omni_tsf_forecasting_engine", "OmniTSFForecastingEngine"),
        ("system.omni_uva_dl_course_engine", "OmniUVADeepLearningEngine"),
    ]

    total = len(engines)
    passed = 0

    for module_path, class_name in engines:
        try:
            mod = __import__(module_path, fromlist=[class_name])
            cls = getattr(mod, class_name)
            instance = cls()
            diag = instance.diagnostics()
            status_ok = diag.get("status") == "operational"
            engine_name = diag.get("engine", class_name)
            if status_ok:
                passed += 1
                print(f"  [OK] {engine_name:<35} -> OPERATIONAL (v{diag.get('version', '?')})")
            else:
                print(f"  [FAIL] {engine_name:<35} -> FAILED (status={diag.get('status')})")
        except Exception as exc:
            print(f"  [FAIL] {class_name:<35} -> IMPORT ERROR: {exc}")

    print(f"\n{'='*60}")
    print(f"  Batch 5 Diagnostics: {passed}/{total} engines operational")
    print(f"{'='*60}")
    return passed == total

if __name__ == "__main__":
    success = run_batch5_diagnostics()
    sys.exit(0 if success else 1)
