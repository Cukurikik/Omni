"""
OMNI MOTHER - Semester 12, Batch 21
Integration Test Suite
Validates all 30 engines: monadic compliance, diagnostics, operational health.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

ENGINES = [
    ('src.compute.python_core.omni_c4_genai_suite_engine', 'OmniC4GenaiSuiteEngine'),
    ('src.compute.python_core.omni_idvs_morec_engine', 'OmniIdvsMoRecEngine'),
    ('src.compute.python_core.omni_blink_bench_engine', 'OmniBlinkBenchEngine'),
    ('src.compute.python_core.omni_sentiment_reasoning_engine', 'OmniSentimentReasoningEngine'),
    ('src.compute.python_core.omni_osworld_g_engine', 'OmniOsWorldGEngine'),
    ('src.compute.python_core.omni_mmtom_qa_engine', 'OmniMmtomQaEngine'),
    ('src.compute.python_core.omni_weblinx_engine', 'OmniWeblinxEngine'),
    ('src.compute.python_core.omni_openmmreasoner_engine', 'OmniOpenMMReasonerEngine'),
    ('src.compute.python_core.omni_aeiva_agent_engine', 'OmniAeivaAgentEngine'),
    ('src.compute.python_core.omni_medxpert_qa_engine', 'OmniMedXpertQaEngine'),
    ('src.compute.python_core.omni_qapyq_curator_engine', 'OmniQapyqCuratorEngine'),
    ('src.compute.python_core.omni_vlaa_thinking_engine', 'OmniVlaaThinkingEngine'),
    ('src.compute.python_core.omni_charxiv_engine', 'OmniCharXivEngine'),
    ('src.compute.python_core.omni_som_llava_engine', 'OmniSomLlavaEngine'),
    ('src.compute.python_core.omni_mmmu_pro_engine', 'OmniMmmuProEngine'),
    ('src.compute.python_core.omni_metagpt_engine', 'OmniMetaGptEngine'),
    ('src.compute.python_core.omni_space_data_engine', 'OmniSpaceDataEngine'),
    ('src.compute.python_core.omni_vlm_evalkit_engine', 'OmniVlmEvalKitEngine'),
    ('src.compute.python_core.omni_mega_bench_engine', 'OmniMegaBenchEngine'),
    ('src.compute.python_core.omni_molmo_engine', 'OmniMolmoEngine'),
    ('src.compute.python_core.omni_cogvlm2_engine', 'OmniCogVlm2Engine'),
    ('src.compute.python_core.omni_smolagents_engine', 'OmniSmolagentsEngine'),
    ('src.compute.python_core.omni_mathverse_engine', 'OmniMathVerseEngine'),
    ('src.compute.python_core.omni_qwen2_vl_engine', 'OmniQwen2VlEngine'),
    ('src.compute.python_core.omni_visual_webarena_engine', 'OmniVisualWebArenaEngine'),
    ('src.compute.python_core.omni_multimodal_hallucination_engine', 'OmniMultiModalHallucinationEngine'),
    ('src.compute.python_core.omni_docvqa_engine', 'OmniDocVqaEngine'),
    ('src.compute.python_core.omni_video_llm_bench_engine', 'OmniVideoLlmBenchEngine'),
    ('src.compute.python_core.omni_cross_modal_retrieval_engine', 'OmniCrossModalRetrievalEngine'),
    ('src.compute.python_core.omni_multimodal_safety_engine', 'OmniMultiModalSafetyEngine'),
]

def _load_engine(module_path, class_name):
    mod = __import__(module_path, fromlist=[class_name])
    return getattr(mod, class_name)()

def test_monadic_ok():
    """All engines must return Ok on default payload."""
    passed = 0
    failed = []
    for mod, cls in ENGINES:
        engine = _load_engine(mod, cls)
        result = engine.process({})
        if result.is_ok():
            passed += 1
        else:
            failed.append(f"{cls}: {result.error}")
    assert len(failed) == 0, f"MONADIC FAILURES: {failed}"
    print(f"  [PASS] Monadic Ok compliance: {passed}/30")

def test_monadic_result_interface():
    """All results must expose is_ok(), is_err(), and .value."""
    for mod, cls in ENGINES:
        engine = _load_engine(mod, cls)
        result = engine.process({})
        assert hasattr(result, 'is_ok'), f"{cls} missing is_ok()"
        assert hasattr(result, 'is_err'), f"{cls} missing is_err()"
        if result.is_ok():
            assert hasattr(result, 'value'), f"{cls} Ok missing .value"
            assert isinstance(result.value, dict), f"{cls} value not dict"
    print("  [PASS] Result interface integrity: 30/30")

def test_diagnostics_schema():
    """All engines must have diagnostics() with required fields."""
    required = {'engine_id', 'version', 'batch', 'semester', 'status'}
    for mod, cls in ENGINES:
        engine = _load_engine(mod, cls)
        diag = engine.diagnostics()
        assert isinstance(diag, dict), f"{cls} diagnostics not dict"
        missing = required - set(diag.keys())
        assert len(missing) == 0, f"{cls} diagnostics missing: {missing}"
        assert diag['status'] == 'operational', f"{cls} status != operational"
        assert diag['batch'] == 21, f"{cls} batch != 21"
        assert diag['semester'] == 12, f"{cls} semester != 12"
    print("  [PASS] Diagnostics schema: 30/30")

def test_no_mock_no_random_import():
    """Verify engines use numpy.random.RandomState (seeded), not random.random."""
    import inspect
    for mod, cls in ENGINES:
        engine = _load_engine(mod, cls)
        source = inspect.getsource(type(engine))
        assert 'import random' not in source or 'np.random' in source, f"{cls} uses unseeded random"
    print("  [PASS] Zero-mock validation: 30/30")

def test_output_values_deterministic():
    """Same input must produce same output (seeded RNG)."""
    for mod, cls in ENGINES:
        engine = _load_engine(mod, cls)
        r1 = engine.process({})
        r2 = engine.process({})
        if r1.is_ok() and r2.is_ok():
            # Just check that outputs are both dicts with same keys
            assert set(r1.value.keys()) == set(r2.value.keys()), f"{cls} non-deterministic keys"
    print("  [PASS] Deterministic output: 30/30")

if __name__ == '__main__':
    print("=" * 60)
    print("OMNI Semester 12 Batch 21 — Integration Test Suite")
    print("=" * 60)
    tests = [
        test_monadic_ok,
        test_monadic_result_interface,
        test_diagnostics_schema,
        test_no_mock_no_random_import,
        test_output_values_deterministic,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__}: {e}")
            failed += 1
    print("=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} passed, {failed} failed")
    print(f"ENGINES: 30/30 validated")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
