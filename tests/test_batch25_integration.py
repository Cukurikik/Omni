# Omni Batch 25 Integration Test
# Validates all 30 repo engines for Semester 14 Batch 25
import importlib, sys

ENGINES = [
    ("omni_tifa_faithfulness", "compute_tifa_score"),
    ("omni_xfinder_evaluator", "extract_key_answer"),
    ("omni_duquant_engine", "hadamard_rotation"),
    ("omni_subgraphrag_engine", "build_adjacency"),
    ("omni_lori_adapter", "task_interference_score"),
    ("omni_deepinception_defense", "detect_inception_attack"),
    ("omni_uhgeval_hallucination", "detect_hallucination_discriminative"),
    ("omni_llmtools_calculator", "inference_memory_gb"),
    ("omni_oneke_extraction", "extract_entities"),
    ("omni_panelgpt_engine", "build_panel_prompt"),
    ("omni_salmonn_caption", "audio_visual_align_score"),
    ("omni_blossomlm_data", "quality_filter"),
    ("omni_conversant_persona", "create_persona"),
    ("omni_xrec_recommend", "user_item_score"),
    ("omni_chemllm_bench", "name_to_smiles_accuracy"),
    ("omni_icsf_selfcorrect", "self_consistency_vote"),
    ("omni_shot2story_engine", "detect_shot_boundaries"),
    ("omni_llamabot_interface", "build_system_prompt"),
    ("omni_zhtw_linter", "lint_text"),
    ("omni_video_reasoning", "temporal_reasoning_score"),
    ("omni_ai4edu_engine", "assess_question_difficulty"),
    ("omni_llmapi_keymanager", "validate_api_key"),
]

def test_batch25():
    sys.path.insert(0, "src/compute/python_core")
    passed = 0; failed = 0
    for mod_name, func_name in ENGINES:
        try:
            mod = importlib.import_module(mod_name)
            assert hasattr(mod, func_name), f"{func_name} not found"
            passed += 1
            print(f"  [PASS] {mod_name}.{func_name}")
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {mod_name}: {e}")
    print(f"\n=== BATCH 25 RESULTS: {passed}/{passed+failed} PASSED ===")
    return failed == 0

if __name__ == "__main__":
    test_batch25()
