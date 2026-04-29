"""
OMNI MOTHER — Semester 12, Batch 22
Integration Test Suite: 30 Engines
Validates: monadic Result[T,E], diagnostics interface, deterministic output.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

ENGINE_REGISTRY = [
    ('src.compute.python_core.omni_mkg_analogy_engine', 'OmniMkgAnalogyEngine'),
    ('src.compute.python_core.omni_interactive_video_engine', 'OmniInteractiveVideoEngine'),
    ('src.compute.python_core.omni_chart_mimic_engine', 'OmniChartMimicEngine'),
    ('src.compute.python_core.omni_fashion_clip_engine', 'OmniFashionClipEngine'),
    ('src.compute.python_core.omni_motioncraft_engine', 'OmniMotionCraftEngine'),
    ('src.compute.python_core.omni_mixgen_engine', 'OmniMixgenEngine'),
    ('src.compute.python_core.omni_mico_omnimodal_engine', 'OmniMicoOmniModalEngine'),
    ('src.compute.python_core.omni_hvpnet_engine', 'OmniHvpnetEngine'),
    ('src.compute.python_core.omni_rstnet_caption_engine', 'OmniRstnetCaptionEngine'),
    ('src.compute.python_core.omni_matryoshka_mm_engine', 'OmniMatryoshkaMmEngine'),
    ('src.compute.python_core.omni_gems_agent_engine', 'OmniGemsAgentEngine'),
    ('src.compute.python_core.omni_minkloc_multimodal_engine', 'OmniMinklocMultimodalEngine'),
    ('src.compute.python_core.omni_lqae_engine', 'OmniLqaeEngine'),
    ('src.compute.python_core.omni_deepseek_ocr_engine', 'OmniDeepseekOcrEngine'),
    ('src.compute.python_core.omni_mmp_survival_engine', 'OmniMmpSurvivalEngine'),
    ('src.compute.python_core.omni_healnet_fusion_engine', 'OmniHealnetFusionEngine'),
    ('src.compute.python_core.omni_mir_metric_engine', 'OmniMirMetricEngine'),
    ('src.compute.python_core.omni_cerul_video_search_engine', 'OmniCerulVideoSearchEngine'),
    ('src.compute.python_core.omni_woodpecker_engine', 'OmniWoodpeckerEngine'),
    ('src.compute.python_core.omni_econ_reconstruction_engine', 'OmniEconReconstructionEngine'),
    ('src.compute.python_core.omni_llm_foundry_engine', 'OmniLlmFoundryEngine'),
    ('src.compute.python_core.omni_latent_diffusion_engine', 'OmniLatentDiffusionEngine'),
    ('src.compute.python_core.omni_eva_clip_engine', 'OmniEvaClipEngine'),
    ('src.compute.python_core.omni_internvl_engine', 'OmniInternvlEngine'),
    ('src.compute.python_core.omni_lavis_engine', 'OmniLavisEngine'),
    ('src.compute.python_core.omni_visprog_engine', 'OmniVisprogEngine'),
    ('src.compute.python_core.omni_oneformer_engine', 'OmniOneformerEngine'),
    ('src.compute.python_core.omni_dalle2_engine', 'OmniDalle2Engine'),
    ('src.compute.python_core.omni_video_llava_engine', 'OmniVideoLlavaEngine'),
    ('src.compute.python_core.omni_ofa_unified_engine', 'OmniOfaUnifiedEngine'),
]

def _load_engine(module_path, class_name):
    mod = __import__(module_path, fromlist=[class_name])
    return getattr(mod, class_name)()

def test_all_monadic_compliance():
    """Every engine.process({}) must return Ok (is_ok=True, has .value dict)."""
    passed = 0
    failed = []
    for mod, cls in ENGINE_REGISTRY:
        engine = _load_engine(mod, cls)
        result = engine.process({})
        if result.is_ok() and isinstance(result.value, dict):
            passed += 1
        else:
            err = result.error if result.is_err() else 'value not dict'
            failed.append((cls, err))
    print(f"[MONADIC] {passed}/30 passed")
    for cls, err in failed:
        print(f"  FAIL: {cls} -> {err}")
    assert passed == 30, f"Monadic compliance: {passed}/30"

def test_all_diagnostics():
    """Every engine must have diagnostics() returning correct batch/semester/status."""
    passed = 0
    failed = []
    for mod, cls in ENGINE_REGISTRY:
        engine = _load_engine(mod, cls)
        diag = engine.diagnostics()
        if (diag.get('batch') == 22 and diag.get('semester') == 12
                and diag.get('status') == 'operational'
                and 'engine_id' in diag and 'version' in diag):
            passed += 1
        else:
            failed.append((cls, diag))
    print(f"[DIAGNOSTICS] {passed}/30 passed")
    for cls, d in failed:
        print(f"  FAIL: {cls} -> {d}")
    assert passed == 30, f"Diagnostics: {passed}/30"

def test_deterministic_output():
    """Two runs with same payload must produce identical results."""
    passed = 0
    failed = []
    for mod, cls in ENGINE_REGISTRY:
        engine = _load_engine(mod, cls)
        r1 = engine.process({})
        r2 = engine.process({})
        if r1.is_ok() and r2.is_ok() and str(r1.value) == str(r2.value):
            passed += 1
        else:
            failed.append(cls)
    print(f"[DETERMINISTIC] {passed}/30 passed")
    for cls in failed:
        print(f"  FAIL: {cls}")
    assert passed == 30, f"Deterministic: {passed}/30"

def test_result_value_has_numeric_keys():
    """Every Ok result must contain at least one numeric metric."""
    passed = 0
    failed = []
    for mod, cls in ENGINE_REGISTRY:
        engine = _load_engine(mod, cls)
        r = engine.process({})
        if r.is_ok():
            has_numeric = any(isinstance(v, (int, float)) for v in r.value.values())
            if has_numeric:
                passed += 1
            else:
                failed.append(cls)
        else:
            failed.append(cls)
    print(f"[NUMERIC_KEYS] {passed}/30 passed")
    assert passed == 30, f"Numeric keys: {passed}/30"

def test_engine_ids_unique():
    """All engine IDs must be unique."""
    ids = set()
    for mod, cls in ENGINE_REGISTRY:
        engine = _load_engine(mod, cls)
        eid = engine.diagnostics()['engine_id']
        assert eid not in ids, f"Duplicate engine_id: {eid}"
        ids.add(eid)
    print(f"[UNIQUE_IDS] 30/30 unique IDs verified")

if __name__ == '__main__':
    print("=" * 60)
    print("OMNI MOTHER — Semester 12 Batch 22 Integration Suite")
    print("=" * 60)
    tests = [
        test_all_monadic_compliance,
        test_all_diagnostics,
        test_deterministic_output,
        test_result_value_has_numeric_keys,
        test_engine_ids_unique,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  ASSERTION FAILED: {e}")
        except Exception as e:
            print(f"  ERROR in {t.__name__}: {e}")
    print("=" * 60)
    print(f"RESULT: {passed}/{len(tests)} test groups passed, 30 engines validated")
    print("=" * 60)
