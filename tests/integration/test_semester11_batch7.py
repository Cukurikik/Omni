import pytest
from src.compute.python_core.omni_python_developer_profile_engine import OmniPythonDeveloperProfileEngine
from src.compute.python_core.omni_saas_content_generation_engine import OmniSAASContentGenerationEngine
from src.compute.python_core.omni_pymol_molecular_docking_engine import OmniPymolMolecularDockingEngine
from src.compute.python_core.omni_github_repository_analyzer_engine import OmniGithubRepositoryAnalyzerEngine
from src.compute.python_core.omni_cpp_algorithm_analysis_engine import OmniCPPAlgorithmAnalysisEngine
from src.compute.python_core.omni_presentation_blog_engine import OmniPresentationBlogEngine
from src.compute.python_core.omni_fast_2d_game_engine import OmniFast2DGameEngine
from src.compute.python_core.omni_pied_piper_ai_engine import OmniPiedPiperAIEngine
from src.compute.python_core.omni_humanscript_interpreter_engine import OmniHumanscriptInterpreterEngine
from src.compute.python_core.omni_micro_blog_generator_engine import OmniMicroBlogGeneratorEngine

# ---------------------------------------------------------
# ENGINE 1: OmniPythonDeveloperProfileEngine
# ---------------------------------------------------------
def test_python_dev_diagnostics():
    en = OmniPythonDeveloperProfileEngine()
    assert en.diagnostics()["status"] == "operational"

def test_python_dev_viable():
    en = OmniPythonDeveloperProfileEngine(1000.0)
    res = en.model_api_route_traffic_viability({"/a": 500.0, "/b": 400.0})
    assert res.is_ok()
    data = res.unwrap()
    assert data["is_infrastructure_stable"] is True
    assert data["overall_utilization_percentage"] == 90.0
    assert len(data["diagnostics_routing_limit"]["active_routes"]) == 2

def test_python_dev_throttled():
    en = OmniPythonDeveloperProfileEngine(1000.0)
    res = en.model_api_route_traffic_viability({"/a": 600.0, "/b": 500.0})
    assert res.is_ok()
    data = res.unwrap()
    assert data["is_infrastructure_stable"] is False
    assert "/a" in data["diagnostics_routing_limit"]["active_routes"]
    assert "/b" in data["diagnostics_routing_limit"]["throttled_routes"]

def test_python_dev_empty():
    en = OmniPythonDeveloperProfileEngine()
    assert not en.model_api_route_traffic_viability({}).is_ok()

def test_python_dev_negative_traffic():
    en = OmniPythonDeveloperProfileEngine()
    # The engine catches negative internally or evaluates?
    # Logic bounds checks if total_traffic < 0
    res = en.model_api_route_traffic_viability({"/a": -100.0})
    assert not res.is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniSAASContentGenerationEngine
# ---------------------------------------------------------
def test_saas_diagnostics():
    en = OmniSAASContentGenerationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_saas_estimation():
    en = OmniSAASContentGenerationEngine(1.5)
    # len=12 (12//4 = 3 tokens). len=1 (1//4 = 0 -> max(1,0)=1 token)
    docs = ["Hello world!", "A"]
    res = en.estimate_token_generation_timeline(docs)
    assert res.is_ok()
    data = res.unwrap()
    assert data["estimated_llm_vectors"] == 4
    assert data["projected_latency_seconds"] == 0.006

def test_saas_empty():
    en = OmniSAASContentGenerationEngine()
    assert not en.estimate_token_generation_timeline([]).is_ok()

def test_saas_invalid_type():
    en = OmniSAASContentGenerationEngine()
    assert not en.estimate_token_generation_timeline([123]).is_ok()

def test_saas_large_text():
    en = OmniSAASContentGenerationEngine(1.0)
    res = en.estimate_token_generation_timeline(["A" * 400])
    data = res.unwrap()
    assert data["estimated_llm_vectors"] == 100
    assert data["tasks_latency_ms"][0] == 100.0

# ---------------------------------------------------------
# ENGINE 3: OmniPymolMolecularDockingEngine
# ---------------------------------------------------------
def test_pymol_diagnostics():
    en = OmniPymolMolecularDockingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_pymol_no_clash():
    en = OmniPymolMolecularDockingEngine(1.2)
    l = [[0.0, 0.0, 0.0]]
    r = [[5.0, 5.0, 5.0]]
    res = en.compute_cartesian_docking_clashes(l, r)
    assert res.is_ok()
    data = res.unwrap()
    assert data["total_clashes"] == 0
    assert data["is_viable_docking"] is True

def test_pymol_clash_detected():
    en = OmniPymolMolecularDockingEngine(2.0)
    l = [[0.0, 0.0, 0.0]]
    r = [[1.0, 0.0, 0.0]]
    res = en.compute_cartesian_docking_clashes(l, r)
    assert res.is_ok()
    assert res.unwrap()["total_clashes"] == 1

def test_pymol_invalid_dimension():
    en = OmniPymolMolecularDockingEngine()
    assert not en.compute_cartesian_docking_clashes([[0.0, 0.0]], [[0.0, 0.0, 0.0]]).is_ok()

def test_pymol_empty():
    en = OmniPymolMolecularDockingEngine()
    assert not en.compute_cartesian_docking_clashes([], []).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniGithubRepositoryAnalyzerEngine
# ---------------------------------------------------------
def test_github_diagnostics():
    en = OmniGithubRepositoryAnalyzerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_github_analysis():
    en = OmniGithubRepositoryAnalyzerEngine(2)
    files = {
        "m.py": "a\nb\nc",  # 3 lines -> bloat 1
        "r.md": "hi"         # 1 line -> no bloat
    }
    res = en.analyze_repository_metrics(files)
    assert res.is_ok()
    data = res.unwrap()
    assert data["metrics"]["total_computed_lines"] == 4
    assert data["architectural_warnings"]["bloated_files_detected"] == 1
    assert data["language_distribution"]["py"] == 1

def test_github_empty():
    en = OmniGithubRepositoryAnalyzerEngine()
    assert not en.analyze_repository_metrics({}).is_ok()

def test_github_non_string():
    en = OmniGithubRepositoryAnalyzerEngine()
    assert not en.analyze_repository_metrics({"m.py": 123}).is_ok()

def test_github_no_bloat():
    en = OmniGithubRepositoryAnalyzerEngine(100)
    res = en.analyze_repository_metrics({"a.c": "int main(){}"})
    assert res.unwrap()["architectural_warnings"]["bloated_files_detected"] == 0

# ---------------------------------------------------------
# ENGINE 5: OmniCPPAlgorithmAnalysisEngine
# ---------------------------------------------------------
def test_cpp_diagnostics():
    en = OmniCPPAlgorithmAnalysisEngine()
    assert en.diagnostics()["status"] == "operational"

def test_cpp_binary_search_valid():
    en = OmniCPPAlgorithmAnalysisEngine()
    # size 100, target 25
    res = en.execute_binary_search_complexity(100, 25)
    assert res.is_ok()
    data = res.unwrap()
    # 0..99
    # M1 = 49 (tgt < 49) right=48
    # M2 = 24 (tgt > 24) left=25
    # M3 = 36 (tgt < 36) right=35
    # M4 = 30 (tgt < 30) right=29
    # M5 = 27 (tgt < 27) right=26
    # M6 = 25 (found)
    assert data["computed_steps_taken"] == 6
    assert data["theoretical_max_steps"] == 7

def test_cpp_binary_search_out_of_bounds():
    en = OmniCPPAlgorithmAnalysisEngine()
    assert not en.execute_binary_search_complexity(100, 150).is_ok()

def test_cpp_binary_search_negative_size():
    en = OmniCPPAlgorithmAnalysisEngine()
    assert not en.execute_binary_search_complexity(-5, 0).is_ok()

def test_cpp_binary_search_element_zero():
    en = OmniCPPAlgorithmAnalysisEngine()
    # size 1, target 0 -> gets it in 1
    res = en.execute_binary_search_complexity(1, 0)
    assert res.unwrap()["computed_steps_taken"] == 1

# ---------------------------------------------------------
# ENGINE 6: OmniPresentationBlogEngine
# ---------------------------------------------------------
def test_blog_diagnostics():
    en = OmniPresentationBlogEngine()
    assert en.diagnostics()["status"] == "operational"

def test_blog_sorting():
    en = OmniPresentationBlogEngine()
    arts = [{"title": "Old", "date": "2020-01-01"}, {"title": "New", "date": "2021-01-01"}]
    res = en.sequence_chronological_blog_matrix(arts)
    assert res.is_ok()
    data = res.unwrap()
    assert data["structured_chronological_sequence"] == ["New", "Old"]
    assert data["timeline_days_gaps_between_articles"][0] == 366

def test_blog_empty():
    en = OmniPresentationBlogEngine()
    assert not en.sequence_chronological_blog_matrix([]).is_ok()

def test_blog_missing_fields():
    en = OmniPresentationBlogEngine()
    assert not en.sequence_chronological_blog_matrix([{"title": "x"}]).is_ok()

def test_blog_bad_date_format():
    en = OmniPresentationBlogEngine()
    # Natively handles bad dates via topological try-catch gaps logic
    res = en.sequence_chronological_blog_matrix([{"title": "a", "date": "bad"}, {"title": "b", "date": "worse"}])
    assert res.unwrap()["timeline_days_gaps_between_articles"][0] == "Unparseable Temporal Gap"

# ---------------------------------------------------------
# ENGINE 7: OmniFast2DGameEngine
# ---------------------------------------------------------
def test_2d_diagnostics():
    en = OmniFast2DGameEngine()
    assert en.diagnostics()["status"] == "operational"

def test_2d_collision_overlap():
    en = OmniFast2DGameEngine()
    a = {"x": 0.0, "y": 0.0, "width": 10.0, "height": 10.0, "id": 1}
    b = {"x": 5.0, "y": 5.0, "width": 10.0, "height": 10.0, "id": 2}
    res = en.compute_aabb_collisions(a, b)
    assert res.is_ok()
    assert res.unwrap()["collision_detected"] is True

def test_2d_collision_miss():
    en = OmniFast2DGameEngine()
    a = {"x": 0.0, "y": 0.0, "width": 10.0, "height": 10.0, "id": 1}
    b = {"x": 20.0, "y": 20.0, "width": 10.0, "height": 10.0, "id": 2}
    res = en.compute_aabb_collisions(a, b)
    assert res.unwrap()["collision_detected"] is False

def test_2d_invalid_dimension():
    en = OmniFast2DGameEngine()
    a = {"x": 0.0, "y": 0.0, "width": -5.0, "height": 10.0, "id": 1}
    b = {"x": 20.0, "y": 20.0, "width": 10.0, "height": 10.0, "id": 2}
    assert not en.compute_aabb_collisions(a, b).is_ok()

def test_2d_missing_keys():
    en = OmniFast2DGameEngine()
    assert not en.compute_aabb_collisions({"x": 0}, {"y": 0}).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniPiedPiperAIEngine
# ---------------------------------------------------------
def test_pied_piper_diagnostics():
    en = OmniPiedPiperAIEngine()
    assert en.diagnostics()["status"] == "operational"

def test_pied_piper_compression():
    en = OmniPiedPiperAIEngine(0.0)
    res = en.execute_middle_out_compression_ratios("A" * 1000)
    assert res.is_ok()
    data = res.unwrap()
    assert data["compression_ratio_multiplier"] > 1.0 # 1000 As compress very well
    assert data["weissman_score_metrics"]["target_met"] is True

def test_pied_piper_empty():
    en = OmniPiedPiperAIEngine()
    assert not en.execute_middle_out_compression_ratios("").is_ok()

def test_pied_piper_poor_compression():
    import os
    en = OmniPiedPiperAIEngine(10.0) # HIGH target
    rand_data = os.urandom(100).hex() # basically random
    res = en.execute_middle_out_compression_ratios(rand_data)
    data = res.unwrap()
    # Random hex won't compress well enough to meet high weissman
    assert data["weissman_score_metrics"]["target_met"] is False

def test_pied_piper_short_string():
    en = OmniPiedPiperAIEngine(0.1)
    res = en.execute_middle_out_compression_ratios("hello")
    # Zlib overhead makes compressed size > original size for tiny strings
    assert res.unwrap()["compression_ratio_multiplier"] < 1.0

# ---------------------------------------------------------
# ENGINE 9: OmniHumanscriptInterpreterEngine
# ---------------------------------------------------------
def test_humanscript_diagnostics():
    en = OmniHumanscriptInterpreterEngine()
    assert en.diagnostics()["status"] == "operational"

def test_humanscript_valid():
    en = OmniHumanscriptInterpreterEngine()
    code = "DEFINE x AS 100\nTELL x\nTELL hello"
    res = en.evaluate_syntactic_tokens(code)
    assert res.is_ok()
    data = res.unwrap()
    assert data["computed_memory_state"]["x"] == "100"
    assert "OUT: 100" in data["execution_trace_arrays"]
    assert "OUT: hello" in data["execution_trace_arrays"]

def test_humanscript_empty():
    en = OmniHumanscriptInterpreterEngine()
    assert not en.evaluate_syntactic_tokens("").is_ok()

def test_humanscript_invalid_syntax():
    en = OmniHumanscriptInterpreterEngine()
    assert not en.evaluate_syntactic_tokens("DEFINE x TO 100").is_ok()

def test_humanscript_unknown_keyword():
    en = OmniHumanscriptInterpreterEngine()
    assert not en.evaluate_syntactic_tokens("JUMP 10").is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniMicroBlogGeneratorEngine
# ---------------------------------------------------------
def test_microblog_diagnostics():
    en = OmniMicroBlogGeneratorEngine()
    assert en.diagnostics()["status"] == "operational"

def test_microblog_compilation():
    en = OmniMicroBlogGeneratorEngine("<t>{title}</t><c>{content}</c>")
    entries = [{"title": "A", "content": "B"}, {"title": "X Y", "content": "Z"}]
    res = en.compile_static_html_artifacts(entries)
    assert res.is_ok()
    data = res.unwrap()
    assert data["total_artifacts_compiled"] == 2
    assert data["compiled_matrix"][0]["compiled_document"] == "<t>A</t><c>B</c>"
    assert data["compiled_matrix"][1]["id"] == "x_y"

def test_microblog_empty():
    en = OmniMicroBlogGeneratorEngine()
    assert not en.compile_static_html_artifacts([]).is_ok()

def test_microblog_missing_keys():
    en = OmniMicroBlogGeneratorEngine()
    assert not en.compile_static_html_artifacts([{"title": "Only"}]).is_ok()

def test_microblog_byte_size():
    en = OmniMicroBlogGeneratorEngine("{title}")
    res = en.compile_static_html_artifacts([{"title": "abc", "content": "1"}])
    assert res.unwrap()["compiled_matrix"][0]["html_byte_size"] == 3
