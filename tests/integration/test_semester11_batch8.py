import pytest
from src.compute.python_core.omni_comp_neuro_cookbook_engine import OmniCompNeuroCookbookEngine
from src.compute.python_core.omni_cine_view_catalog_engine import OmniCineViewCatalogEngine
from src.compute.python_core.omni_hug_ai_logic_engine import OmniHugAILogicEngine
from src.compute.python_core.omni_typescript_cv_parser_engine import OmniTypeScriptCVParserEngine
from src.compute.python_core.omni_flash_vsr_video_upscale_engine import OmniFlashVSRVideoUpscaleEngine
from src.compute.python_core.omni_sow_project_management_engine import OmniSOWProjectManagementEngine
from src.compute.python_core.omni_verilog_fpga_emulator_engine import OmniVerilogFPGAEmulatorEngine
from src.compute.python_core.omni_nuggets_curation_engine import OmniNuggetsCurationEngine
from src.compute.python_core.omni_ai_context_doc_methodology_engine import OmniAIContextDocMethodologyEngine
from src.compute.python_core.omni_systemdev_refcards_engine import OmniSystemdevRefcardsEngine

# ---------------------------------------------------------
# ENGINE 1: OmniCompNeuroCookbookEngine
# ---------------------------------------------------------
def test_comp_neuro_diagnostics():
    en = OmniCompNeuroCookbookEngine()
    assert en.diagnostics()["status"] == "operational"

def test_comp_neuro_valid():
    en = OmniCompNeuroCookbookEngine()
    txt = "This is the Introduction, then the Methodology, and finally the Results."
    res = en.validate_cookbook_structure(txt)
    assert res.is_ok()
    data = res.unwrap()
    assert data["guideline_compliance"] is True
    assert data["compliance_score_ratio"] == 1.0

def test_comp_neuro_missing_section():
    en = OmniCompNeuroCookbookEngine()
    txt = "Just some Methodology."
    res = en.validate_cookbook_structure(txt)
    assert res.is_ok()
    data = res.unwrap()
    assert data["guideline_compliance"] is False
    assert "Results" in data["sections_diagnostics"]["missing"]

def test_comp_neuro_custom_sections():
    en = OmniCompNeuroCookbookEngine(["Abstract", "Conclusion"])
    res = en.validate_cookbook_structure("Abstract of the paper.")
    assert res.unwrap()["compliance_score_ratio"] == 0.5

def test_comp_neuro_empty():
    en = OmniCompNeuroCookbookEngine()
    assert not en.validate_cookbook_structure("").is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniCineViewCatalogEngine
# ---------------------------------------------------------
def test_cine_view_diagnostics():
    en = OmniCineViewCatalogEngine()
    assert en.diagnostics()["status"] == "operational"

def test_cine_view_sorting_and_filtering():
    en = OmniCineViewCatalogEngine(8.0)
    films = [{"title": "Epic", "rating": 9.0}, {"title": "Bad", "rating": 4.0}]
    res = en.compute_catalog_rankings(films)
    assert res.is_ok()
    data = res.unwrap()
    assert data["top_ranked_film"] == "Epic"
    assert "Epic" in data["premium_tier_films"]
    assert "Bad" not in data["premium_tier_films"]
    assert data["average_catalog_rating"] == 6.5

def test_cine_view_empty():
    en = OmniCineViewCatalogEngine()
    assert not en.compute_catalog_rankings([]).is_ok()

def test_cine_view_missing_keys():
    en = OmniCineViewCatalogEngine()
    assert not en.compute_catalog_rankings([{"name": "NoRating"}]).is_ok()

def test_cine_view_string_ratings():
    en = OmniCineViewCatalogEngine(5.0)
    # Native float casting structurally parses JSON string metrics
    res = en.compute_catalog_rankings([{"title": "Ok", "rating": "5.5"}])
    assert res.unwrap()["top_ranked_film"] == "Ok"

# ---------------------------------------------------------
# ENGINE 3: OmniHugAILogicEngine
# ---------------------------------------------------------
def test_hug_ai_diagnostics():
    en = OmniHugAILogicEngine()
    assert en.diagnostics()["status"] == "operational"

def test_hug_ai_straight_path():
    en = OmniHugAILogicEngine()
    topo = {"A": "B", "B": "C", "C": "END"}
    res = en.execute_agent_task_routing(topo, "A")
    assert res.is_ok()
    data = res.unwrap()
    assert data["routing_status"] == "COMPLETED_TERMINUS"
    assert data["nodes_traversed"] == ["A", "B", "C"]

def test_hug_ai_circular():
    en = OmniHugAILogicEngine()
    topo = {"A": "B", "B": "A"}
    res = en.execute_agent_task_routing(topo, "A")
    assert res.is_ok()
    assert res.unwrap()["routing_status"] == "CIRCULAR_LIMIT_REACHED"

def test_hug_ai_hop_limit():
    en = OmniHugAILogicEngine(2)
    topo = {"A": "B", "B": "C", "C": "D", "D": "END"}
    res = en.execute_agent_task_routing(topo, "A")
    assert res.is_ok()
    assert res.unwrap()["routing_status"] == "HOP_LIMIT_EXCEEDED"

def test_hug_ai_invalid_start():
    en = OmniHugAILogicEngine()
    assert not en.execute_agent_task_routing({"A": "END"}, "X").is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniTypeScriptCVParserEngine
# ---------------------------------------------------------
def test_cv_parser_diagnostics():
    en = OmniTypeScriptCVParserEngine()
    assert en.diagnostics()["status"] == "operational"

def test_cv_parser_valid():
    en = OmniTypeScriptCVParserEngine(10)
    blocks = [
        {"role": "Dev", "year": 2020, "desc": "Wrote some python code."},
        {"role": "Lead", "year": 2022, "desc": "Managed the entire team."}
    ]
    res = en.parse_cv_experience_blocks(blocks)
    assert res.is_ok()
    data = res.unwrap()
    assert data["is_structurally_valid"] is True
    assert data["chronological_role_sequence"] == ["Lead", "Dev"]

def test_cv_parser_short_desc():
    en = OmniTypeScriptCVParserEngine(50)
    blocks = [{"role": "Dev", "year": 2020, "desc": "Too short."}]
    res = en.parse_cv_experience_blocks(blocks)
    assert res.unwrap()["is_structurally_valid"] is False
    assert "Dev" in res.unwrap()["flagged_short_descriptions"]

def test_cv_parser_empty():
    en = OmniTypeScriptCVParserEngine()
    assert not en.parse_cv_experience_blocks([]).is_ok()

def test_cv_parser_missing_keys():
    en = OmniTypeScriptCVParserEngine()
    assert not en.parse_cv_experience_blocks([{"role": "X"}]).is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniFlashVSRVideoUpscaleEngine
# ---------------------------------------------------------
def test_flash_vsr_diagnostics():
    en = OmniFlashVSRVideoUpscaleEngine()
    assert en.diagnostics()["status"] == "operational"

def test_flash_vsr_valid_upscale():
    en = OmniFlashVSRVideoUpscaleEngine(1.0)
    # 1080 -> 2160 (2x) -> 2^2 = 4x base time. Base=15ms. -> 60ms latency per frame.
    res = en.compute_upscaling_latency_bounds(10, 1080, 2160)
    assert res.is_ok()
    data = res.unwrap()
    assert data["upscale_ratio_multiplier"] == 2.0
    assert data["latency_per_frame_ms"] == 60.0
    assert data["realtime_playback_supported"] is False # 60ms > 33.33ms

def test_flash_vsr_downscale_rejected():
    en = OmniFlashVSRVideoUpscaleEngine()
    assert not en.compute_upscaling_latency_bounds(10, 2160, 1080).is_ok()

def test_flash_vsr_zero_frames():
    en = OmniFlashVSRVideoUpscaleEngine()
    assert not en.compute_upscaling_latency_bounds(0, 1080, 2160).is_ok()

def test_flash_vsr_realtime_capable():
    en = OmniFlashVSRVideoUpscaleEngine(1.0)
    # 720 -> 1080 (1.5x) -> 1.5^2 = 2.25x. -> 33.75ms (just misses).
    # 1080 -> 1440 (1.33x) -> 1.76x. -> 26.5ms (realtime!)
    res = en.compute_upscaling_latency_bounds(10, 1080, 1440)
    assert res.unwrap()["realtime_playback_supported"] is True

# ---------------------------------------------------------
# ENGINE 6: OmniSOWProjectManagementEngine
# ---------------------------------------------------------
def test_sow_diagnostics():
    en = OmniSOWProjectManagementEngine()
    assert en.diagnostics()["status"] == "operational"

def test_sow_cost_calculation():
    en = OmniSOWProjectManagementEngine(100.0)
    mods = [{"feature": "A", "estimated_hours": 10}, {"feature": "B", "estimated_hours": 20}]
    res = en.evaluate_cost_estimation_metrics(mods)
    assert res.is_ok()
    data = res.unwrap()
    assert data["raw_total_hours"] == 30.0
    assert data["contingency_hours_buffer"] == 4.5
    assert data["total_estimated_budget"] == 3450.0

def test_sow_empty():
    en = OmniSOWProjectManagementEngine()
    assert not en.evaluate_cost_estimation_metrics([]).is_ok()

def test_sow_missing_keys():
    en = OmniSOWProjectManagementEngine()
    assert not en.evaluate_cost_estimation_metrics([{"feature": "A"}]).is_ok()

def test_sow_negative_hours():
    en = OmniSOWProjectManagementEngine()
    assert not en.evaluate_cost_estimation_metrics([{"feature": "A", "estimated_hours": -5}]).is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniVerilogFPGAEmulatorEngine
# ---------------------------------------------------------
def test_fpga_diagnostics():
    en = OmniVerilogFPGAEmulatorEngine()
    assert en.diagnostics()["status"] == "operational"

def test_fpga_add_carry():
    # 8-bit limit: max is 255
    en = OmniVerilogFPGAEmulatorEngine(8)
    res = en.compute_alu_bitwise_operations(200, 100, "ADD")
    assert res.is_ok()
    data = res.unwrap()
    assert data["bitwise_computation_result"] == 44 # 300 % 256
    assert data["overflow_carry_flag"] == 1

def test_fpga_and():
    en = OmniVerilogFPGAEmulatorEngine(8)
    res = en.compute_alu_bitwise_operations(0x0F, 0xAA, "AND")
    assert res.unwrap()["bitwise_computation_result"] == 0x0A

def test_fpga_invalid_op():
    en = OmniVerilogFPGAEmulatorEngine()
    assert not en.compute_alu_bitwise_operations(1, 1, "DIV").is_ok()

def test_fpga_truncate():
    en = OmniVerilogFPGAEmulatorEngine(4) # max 15
    res = en.compute_alu_bitwise_operations(30, 0, "ADD")
    # 30 truncated to 4 bits is 14
    assert res.unwrap()["diagnostics_register_limits"]["operand_a_truncated"] == 14

# ---------------------------------------------------------
# ENGINE 8: OmniNuggetsCurationEngine
# ---------------------------------------------------------
def test_nuggets_diagnostics():
    en = OmniNuggetsCurationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nuggets_curation():
    en = OmniNuggetsCurationEngine(["apple", "banana"])
    txts = ["I ate an APPLE today.", "No fruit here.", "Banana split!"]
    res = en.extract_insight_metrics(txts)
    assert res.is_ok()
    data = res.unwrap()
    assert data["insightful_nuggets_found"] == 2
    assert "unique_vocabulary_size" in data

def test_nuggets_empty():
    en = OmniNuggetsCurationEngine()
    assert not en.extract_insight_metrics([]).is_ok()

def test_nuggets_non_string():
    en = OmniNuggetsCurationEngine()
    assert not en.extract_insight_metrics([123]).is_ok()

def test_nuggets_zero_hits():
    en = OmniNuggetsCurationEngine(["zebra"])
    res = en.extract_insight_metrics(["hello world"])
    assert res.unwrap()["insightful_nuggets_found"] == 0

# ---------------------------------------------------------
# ENGINE 9: OmniAIContextDocMethodologyEngine
# ---------------------------------------------------------
def test_context_doc_diagnostics():
    en = OmniAIContextDocMethodologyEngine()
    assert en.diagnostics()["status"] == "operational"

def test_context_doc_traversal():
    en = OmniAIContextDocMethodologyEngine()
    tree = {
        "A": "text A",
        "B": {
            "C": "text C"
        }
    }
    res = en.execute_documentation_tree_traversal(tree)
    assert res.is_ok()
    data = res.unwrap()
    assert data["total_structural_nodes"] == 3 # A, B, C
    assert "text A" in data["extracted_text_blocks"]
    assert "text C" in data["extracted_text_blocks"]

def test_context_doc_depth_limit():
    en = OmniAIContextDocMethodologyEngine(1)
    # depth 0 is root, depth 1 is B, depth 2 is D (will fail limit)
    tree = {"A": {"B": {"D": "fail"}}}
    assert not en.execute_documentation_tree_traversal(tree).is_ok()

def test_context_doc_non_dict():
    en = OmniAIContextDocMethodologyEngine()
    assert not en.execute_documentation_tree_traversal("not a dict").is_ok()

def test_context_doc_empty_dict():
    en = OmniAIContextDocMethodologyEngine()
    res = en.execute_documentation_tree_traversal({})
    assert res.unwrap()["total_structural_nodes"] == 0

# ---------------------------------------------------------
# ENGINE 10: OmniSystemdevRefcardsEngine
# ---------------------------------------------------------
def test_refcards_diagnostics():
    en = OmniSystemdevRefcardsEngine()
    assert en.diagnostics()["status"] == "operational"

def test_refcards_valid():
    en = OmniSystemdevRefcardsEngine()
    cards = [{"question": "Q?", "answer": "Yes!"}, {"question": "Long question?", "answer": "No"}]
    res = en.evaluate_study_card_geometries(cards)
    assert res.is_ok()
    data = res.unwrap()
    assert data["total_cards_processed"] == 2
    # Second card has answer len=2, question len=14. 2 < 14*0.5 -> Flagged
    assert 1 in data["flagged_cards_short_answers_indexes"]

def test_refcards_empty():
    en = OmniSystemdevRefcardsEngine()
    assert not en.evaluate_study_card_geometries([]).is_ok()

def test_refcards_missing_keys():
    en = OmniSystemdevRefcardsEngine()
    assert not en.evaluate_study_card_geometries([{"q": 1}]).is_ok()

def test_refcards_numeric_types():
    en = OmniSystemdevRefcardsEngine()
    assert en.evaluate_study_card_geometries([{"question": 100, "answer": 500}]).is_ok()
