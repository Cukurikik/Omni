import pytest
from src.compute.python_core.omni_symfony_resume_engine import OmniSymfonyResumeEngine
from src.compute.python_core.omni_ubuntu_dev_settings_engine import OmniUbuntuDevSettingsEngine
from src.compute.python_core.omni_fiber_auth_session_engine import OmniFiberAuthSessionEngine
from src.compute.python_core.omni_desarrollo_web_engine import OmniDesarrolloWebEngine
from src.compute.python_core.omni_joo_arduino_compiler_engine import OmniJooArduinoCompilerEngine
from src.compute.python_core.omni_xbyy_problem_solving_engine import OmniXbyYProblemSolvingEngine
from src.compute.python_core.omni_unicesumar_projects_engine import OmniUnicesumarProjectsEngine
from src.compute.python_core.omni_nexa_research_agent_engine import OmniNexaResearchAgentEngine
from src.compute.python_core.omni_glsatellite_demo_engine import OmniGLSatelliteDemoEngine
from src.compute.python_core.omni_norad_database_parser_engine import OmniNoradDatabaseParserEngine

# ---------------------------------------------------------
# ENGINE 1: OmniSymfonyResumeEngine
# ---------------------------------------------------------
def test_symfony_resume_diagnostics():
    en = OmniSymfonyResumeEngine()
    assert en.diagnostics()["status"] == "operational"

def test_symfony_resume_valid():
    en = OmniSymfonyResumeEngine(5)
    data = {
        "name": "Alex",
        "sections": [
            {"title": "Experience", "length": 150},
            {"title": "Education", "length": 100}
        ]
    }
    res = en.map_resume_structural_nodes(data)
    assert res.is_ok()
    out = res.unwrap()
    assert out["is_structurally_valid"] is True
    assert out["aggregated_content_length_metric"] == 250

def test_symfony_resume_limit_exceeded():
    en = OmniSymfonyResumeEngine(1)
    data = {"name": "Alex", "sections": [{"title": "A"}, {"title": "B"}]}
    assert not en.map_resume_structural_nodes(data).is_ok()

def test_symfony_resume_empty_section():
    en = OmniSymfonyResumeEngine()
    data = {"name": "Alex", "sections": [{"title": "Projects", "length": 0}]}
    res = en.map_resume_structural_nodes(data)
    assert res.unwrap()["is_structurally_valid"] is False
    assert "Projects" in res.unwrap()["flagged_empty_sections"]

def test_symfony_resume_missing_keys():
    en = OmniSymfonyResumeEngine()
    assert not en.map_resume_structural_nodes({"sections": []}).is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniUbuntuDevSettingsEngine
# ---------------------------------------------------------
def test_ubuntu_dev_diagnostics():
    en = OmniUbuntuDevSettingsEngine()
    assert en.diagnostics()["status"] == "operational"

def test_ubuntu_dev_valid():
    en = OmniUbuntuDevSettingsEngine(8192)
    sys = {"os": "ubuntu", "ram_mb": 16000, "packages": ["git", "docker", "curl", "build-essential"]}
    res = en.evaluate_environment_configuration(sys)
    assert res.is_ok()
    assert res.unwrap()["dev_environment_validated"] is True

def test_ubuntu_dev_wrong_os():
    en = OmniUbuntuDevSettingsEngine()
    assert not en.evaluate_environment_configuration({"os": "windows"}).is_ok()

def test_ubuntu_dev_low_ram():
    en = OmniUbuntuDevSettingsEngine(16000)
    sys = {"os": "ubuntu", "ram_mb": 8000}
    res = en.evaluate_environment_configuration(sys)
    assert res.unwrap()["dev_environment_validated"] is False

def test_ubuntu_dev_missing_packages():
    en = OmniUbuntuDevSettingsEngine()
    sys = {"os": "ubuntu", "ram_mb": 16000, "packages": ["git"]}
    res = en.evaluate_environment_configuration(sys)
    assert res.unwrap()["dev_environment_validated"] is False
    assert "docker" in res.unwrap()["missing_native_packages"]

# ---------------------------------------------------------
# ENGINE 3: OmniFiberAuthSessionEngine
# ---------------------------------------------------------
def test_fiber_auth_diagnostics():
    en = OmniFiberAuthSessionEngine()
    assert en.diagnostics()["status"] == "operational"

def test_fiber_auth_valid_session():
    en = OmniFiberAuthSessionEngine(3600)
    tokens = [{"user_id": "u1", "issued_at": 1000}]
    res = en.math_evaluate_token_validity(tokens, current_time_override=2000)
    assert res.is_ok()
    assert "u1" in res.unwrap()["active_users"]

def test_fiber_auth_expired():
    en = OmniFiberAuthSessionEngine(3600)
    tokens = [{"user_id": "u2", "issued_at": 1000}]
    res = en.math_evaluate_token_validity(tokens, current_time_override=5000)
    assert "u2" in res.unwrap()["expired_users"]

def test_fiber_auth_future_token():
    en = OmniFiberAuthSessionEngine()
    tokens = [{"user_id": "u3", "issued_at": 5000}]
    # Issued at 5000, time is 1000 -> negative delta!
    assert not en.math_evaluate_token_validity(tokens, current_time_override=1000).is_ok()

def test_fiber_auth_missing_keys():
    en = OmniFiberAuthSessionEngine()
    assert not en.math_evaluate_token_validity([{"user": "x"}]).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniDesarrolloWebEngine
# ---------------------------------------------------------
def test_desarrollo_web_diagnostics():
    en = OmniDesarrolloWebEngine()
    assert en.diagnostics()["status"] == "operational"

def test_desarrollo_web_valid():
    en = OmniDesarrolloWebEngine(0.5)
    tags = ["<header>", "<main>", "<div>", "<footer>"]
    res = en.validate_web_structural_components(tags)
    assert res.is_ok()
    out = res.unwrap()
    assert out["ratio_compliance_valid"] is True
    assert out["semantic_ratio_metric"] == 0.75 # 3/4

def test_desarrollo_web_low_ratio():
    en = OmniDesarrolloWebEngine(0.8)
    tags = ["<div>", "<span>", "<div>", "<header>"]
    res = en.validate_web_structural_components(tags)
    assert res.unwrap()["ratio_compliance_valid"] is False

def test_desarrollo_web_invalid_string():
    en = OmniDesarrolloWebEngine()
    assert not en.validate_web_structural_components(["header"]).is_ok()

def test_desarrollo_web_empty():
    en = OmniDesarrolloWebEngine()
    assert not en.validate_web_structural_components([]).is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniJooArduinoCompilerEngine
# ---------------------------------------------------------
def test_joo_compiler_diagnostics():
    en = OmniJooArduinoCompilerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_joo_compiler_valid():
    en = OmniJooArduinoCompilerEngine(2048)
    alloc = [{"type": "int16", "count": 100}, {"type": "int8", "count": 50}]
    res = en.execute_bytecode_memory_limits(alloc)
    assert res.is_ok()
    # 100*2 = 200. 50*1 = 50. Total 250.
    assert res.unwrap()["memory_overflow_detected"] is False
    assert res.unwrap()["sram_bytes_allocated"] == 250

def test_joo_compiler_overflow():
    en = OmniJooArduinoCompilerEngine(500)
    alloc = [{"type": "float32", "count": 200}] # 800 bytes
    res = en.execute_bytecode_memory_limits(alloc)
    assert res.unwrap()["memory_overflow_detected"] is True

def test_joo_compiler_invalid_type():
    en = OmniJooArduinoCompilerEngine()
    alloc = [{"type": "magic_type", "count": 10}]
    assert not en.execute_bytecode_memory_limits(alloc).is_ok()

def test_joo_compiler_negative_count():
    en = OmniJooArduinoCompilerEngine()
    assert not en.execute_bytecode_memory_limits([{"type": "int8", "count": -5}]).is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniXbyYProblemSolvingEngine
# ---------------------------------------------------------
def test_xbyy_diagnostics():
    en = OmniXbyYProblemSolvingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_xbyy_valid_stack():
    en = OmniXbyYProblemSolvingEngine(["python"])
    res = en.compute_problem_solution_matrix("backend", "python")
    assert res.is_ok()
    assert res.unwrap()["stack_validation_check"] is True

def test_xbyy_invalid_stack():
    en = OmniXbyYProblemSolvingEngine(["python"])
    res = en.compute_problem_solution_matrix("mobile", "swift")
    assert res.is_ok() # Returns Ok but with error flag
    assert res.unwrap()["stack_validation_check"] is False

def test_xbyy_feasibility_computation():
    en = OmniXbyYProblemSolvingEngine(["react"])
    # webapp vs react. length 6 vs 5. intersection: {e,a}. len 2.
    # maximum length 6. ratio 2/6 = 0.33. score = 100 - 3.3 = ~96.7
    res = en.compute_problem_solution_matrix("webapp", "react")
    assert res.unwrap()["stack_validation_check"] is True
    assert "algebraic_feasibility_score" in res.unwrap()

def test_xbyy_empty():
    en = OmniXbyYProblemSolvingEngine()
    assert not en.compute_problem_solution_matrix("", "go").is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniUnicesumarProjectsEngine
# ---------------------------------------------------------
def test_unicesumar_diagnostics():
    en = OmniUnicesumarProjectsEngine()
    assert en.diagnostics()["status"] == "operational"

def test_unicesumar_pass():
    en = OmniUnicesumarProjectsEngine(7.0)
    scores = [{"student": "Bob", "code_quality": 8.0, "design": 8.0}]
    res = en.evaluate_student_project_grades(scores)
    assert res.is_ok()
    assert "Bob" in res.unwrap()["passing_student_IDs"]

def test_unicesumar_fail():
    en = OmniUnicesumarProjectsEngine(7.0)
    scores = [{"student": "Alice", "code_quality": 5.0, "design": 4.0}]
    res = en.evaluate_student_project_grades(scores)
    assert "Alice" in res.unwrap()["failing_student_IDs"]

def test_unicesumar_out_of_bounds():
    en = OmniUnicesumarProjectsEngine()
    assert not en.evaluate_student_project_grades([{"student": "X", "code_quality": 11, "design": 5}]).is_ok()

def test_unicesumar_missing_keys():
    en = OmniUnicesumarProjectsEngine()
    assert not en.evaluate_student_project_grades([{"student": "A"}]).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniNexaResearchAgentEngine
# ---------------------------------------------------------
def test_nexa_research_diagnostics():
    en = OmniNexaResearchAgentEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nexa_research_high_confidence():
    en = OmniNexaResearchAgentEngine(0.8)
    src = [{"source_url": "test.edu", "peer_reviewed": True, "base_confidence": 0.7}]
    # 0.7 + 0.1 (edu) + 0.05 (peer) = 0.85
    res = en.evaluate_research_source_credibility(src)
    assert res.is_ok()
    assert "test.edu" in res.unwrap()["high_credibility_domains"]

def test_nexa_research_low_confidence():
    en = OmniNexaResearchAgentEngine(0.9)
    src = [{"source_url": "random.com", "peer_reviewed": False, "base_confidence": 0.5}]
    res = en.evaluate_research_source_credibility(src)
    assert "random.com" in res.unwrap()["low_credibility_domains"]

def test_nexa_research_no_url():
    en = OmniNexaResearchAgentEngine()
    assert not en.evaluate_research_source_credibility([{"base_confidence": 0.5}]).is_ok()

def test_nexa_research_empty():
    en = OmniNexaResearchAgentEngine()
    assert not en.evaluate_research_source_credibility([]).is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniGLSatelliteDemoEngine
# ---------------------------------------------------------
def test_glsatellite_diagnostics():
    en = OmniGLSatelliteDemoEngine()
    assert en.diagnostics()["status"] == "operational"

def test_glsatellite_visible():
    en = OmniGLSatelliteDemoEngine(6371)
    obs = {"x": 0, "y": 0, "z": 6371}
    sats = [{"name": "S1", "x": 0, "y": 0, "z": 8000}]
    res = en.calculate_satellite_visibility_limits(obs, sats)
    assert res.is_ok()
    out = res.unwrap()
    assert "S1" in out["simulated_visible_satellites"]
    assert out["Euclidean_distance_matrices"]["S1"] == 1629.0

def test_glsatellite_hidden():
    en = OmniGLSatelliteDemoEngine(6371)
    obs = {"x": 0, "y": 0, "z": 6371}
    sats = [{"name": "S2", "x": 0, "y": 0, "z": -100}] # Below threshold approx limit
    res = en.calculate_satellite_visibility_limits(obs, sats)
    assert "S2" not in res.unwrap()["simulated_visible_satellites"]

def test_glsatellite_missing_coords():
    en = OmniGLSatelliteDemoEngine()
    assert not en.calculate_satellite_visibility_limits({"x": 0}, [{"name": "S"}]).is_ok()

def test_glsatellite_empty_satellites():
    en = OmniGLSatelliteDemoEngine()
    assert not en.calculate_satellite_visibility_limits({"x":0,"y":0,"z":0}, []).is_ok()

# ---------------------------------------------------------
# ENGINE 10: OmniNoradDatabaseParserEngine
# ---------------------------------------------------------
def test_norad_parser_diagnostics():
    en = OmniNoradDatabaseParserEngine()
    assert en.diagnostics()["status"] == "operational"

def test_norad_parser_valid():
    en = OmniNoradDatabaseParserEngine(10)
    # 0123456789
    # 1 25544U X
    lines = ["1 25544U X"]
    res = en.validate_tle_line_boundaries(lines)
    assert res.is_ok()
    data = res.unwrap()
    assert data["is_database_structurally_valid"] is True
    assert "25544" in data["extracted_identifiers_schema"]

def test_norad_parser_invalid_length():
    en = OmniNoradDatabaseParserEngine(10)
    lines = ["too short"]
    res = en.validate_tle_line_boundaries(lines)
    assert res.unwrap()["is_database_structurally_valid"] is False
    assert 0 in res.unwrap()["corrupted_line_indices"]

def test_norad_parser_empty():
    en = OmniNoradDatabaseParserEngine()
    assert not en.validate_tle_line_boundaries([]).is_ok()

def test_norad_parser_non_string():
    en = OmniNoradDatabaseParserEngine()
    assert not en.validate_tle_line_boundaries([123]).is_ok()
