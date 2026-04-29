"""
OMNI MOTHER - Semester 12, Batch 19
Integration Test Suite — 30 Production-Grade Engines
Validates: import, instantiation, process(Ok), diagnostics, monadic compliance
"""
import sys
import os

# Insert OMNI root (c:\Users\IKYY\Downloads\Omni) into sys.path
_OMNI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _OMNI_ROOT not in sys.path:
    sys.path.insert(0, _OMNI_ROOT)


ENGINES = [
    ("omni_mmt_engine", "OmniMmtEngine"),
    ("omni_pigeon_engine", "OmniPigeonEngine"),
    ("omni_bliva_engine", "OmniBlivaEngine"),
    ("omni_magic_engine", "OmniMagicEngine"),
    ("omni_seemore_engine", "OmniSeemoreEngine"),
    ("omni_epnet_engine", "OmniEpnetEngine"),
    ("omni_keras_llm_robot_engine", "OmniKerasLlmRobotEngine"),
    ("omni_cmg_engine", "OmniCmgEngine"),
    ("omni_lighthouse_engine", "OmniLighthouseEngine"),
    ("omni_mcat_engine", "OmniMcatEngine"),
    ("omni_gui_r1_engine", "OmniGuiR1Engine"),
    ("omni_camliflow_engine", "OmniCamliflowEngine"),
    ("omni_rtx_engine", "OmniRtxEngine"),
    ("omni_mantis_engine", "OmniMantisEngine"),
    ("omni_omnifusion_engine", "OmniOmnifusionEngine"),
    ("omni_deepviewagg_engine", "OmniDeepviewaggEngine"),
    ("omni_kaleido_bert_engine", "OmniKaleidoBertEngine"),
    ("omni_motion_anything_engine", "OmniMotionAnythingEngine"),
    ("omni_mplug2_engine", "OmniMplug2Engine"),
    ("omni_deepverse_engine", "OmniDeepverseEngine"),
    ("omni_mmrazor_engine", "OmniMmrazorEngine"),
    ("omni_nystromformer_engine", "OmniNystromformerEngine"),
    ("omni_shape_e_engine", "OmniShapeEEngine"),
    ("omni_videomae_ft_engine", "OmniVideomaeFtEngine"),
    ("omni_posegpt_engine", "OmniPosegptEngine"),
    ("omni_multimodal_mixture_engine", "OmniMultimodalMixtureEngine"),
    ("omni_actionclip_engine", "OmniActionClipEngine"),
    ("omni_docowl_engine", "OmniDocOwlEngine"),
    ("omni_polaris_engine", "OmniPolarisEngine"),
    ("omni_anymal_engine", "OmniAnymalEngine"),
]


def run_tests():
    passed = 0
    failed = 0
    errors = []

    for module_name, class_name in ENGINES:
        test_label = f"test_{class_name}"
        try:
            # 1. Import
            mod = __import__(f"src.compute.python_core.{module_name}", fromlist=[class_name])
            engine_cls = getattr(mod, class_name)

            # 2. Instantiate
            engine = engine_cls()

            # 3. Diagnostics
            diag = engine.diagnostics()
            assert isinstance(diag, dict), f"{class_name}: diagnostics() must return dict"
            assert diag.get("status") == "operational", f"{class_name}: status != operational"
            assert diag.get("engine_id") == class_name, f"{class_name}: engine_id mismatch"
            assert "version" in diag, f"{class_name}: missing version"
            assert diag.get("batch") == 19, f"{class_name}: batch != 19"
            assert diag.get("semester") == 12, f"{class_name}: semester != 12"

            # 4. Process with empty payload
            result = engine.process({})

            # 5. Monadic compliance
            assert hasattr(result, "is_ok"), f"{class_name}: result missing is_ok()"
            assert hasattr(result, "is_err"), f"{class_name}: result missing is_err()"
            assert result.is_ok(), f"{class_name}: process({{}}) returned Err: {getattr(result, 'error', 'unknown')}"
            assert isinstance(result.value, dict), f"{class_name}: result.value must be dict"

            # 6. Result value sanity
            assert len(result.value) > 0, f"{class_name}: result.value is empty"

            passed += 1
            print(f"  PASSED  {test_label}")

        except Exception as e:
            failed += 1
            errors.append((test_label, str(e)))
            print(f"  FAILED  {test_label}: {e}")

    print(f"\n{'='*60}")
    print(f"SEMESTER 12 BATCH 19 INTEGRATION RESULTS")
    print(f"{'='*60}")
    print(f"PASSED: {passed}/{len(ENGINES)}")
    print(f"FAILED: {failed}/{len(ENGINES)}")

    if errors:
        print(f"\nFailed Tests:")
        for name, err in errors:
            print(f"  - {name}: {err}")

    print(f"{'='*60}")
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_tests()
    sys.exit(0 if failed == 0 else 1)
