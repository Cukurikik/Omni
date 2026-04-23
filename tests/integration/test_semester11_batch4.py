import pytest
from src.compute.python_core.omni_virtual_desktop_saas_arbiter_engine import OmniVirtualDesktopSaaSArbiterEngine
from src.compute.python_core.omni_portfolio_static_generation_engine import OmniPortfolioStaticGenerationEngine
from src.compute.python_core.omni_privacy_aware_cyber_threat_engine import OmniPrivacyAwareCyberThreatEngine
from src.compute.python_core.omni_agile_sprint_planner_engine import OmniAgileSprintPlannerEngine
from src.compute.python_core.omni_developer_roadmap_traversal_engine import OmniDeveloperRoadmapTraversalEngine
from src.compute.python_core.omni_video_editor_timeline_engine import OmniVideoEditorTimelineEngine
from src.compute.python_core.omni_python_project_categorization_engine import OmniPythonProjectCategorizationEngine
from src.compute.python_core.omni_whatsapp_communication_bridge_engine import OmniWhatsAppCommunicationBridgeEngine
from src.compute.python_core.omni_godot_entity_simulation_engine import OmniGodotEntitySimulationEngine
from src.compute.python_core.omni_cs253_software_course_matrix_engine import OmniCS253SoftwareCourseMatrixEngine

# ---------------------------------------------------------
# ENGINE 1: OmniVirtualDesktopSaaSArbiterEngine
# ---------------------------------------------------------
def test_desktop_diagnostics():
    en = OmniVirtualDesktopSaaSArbiterEngine(1920, 1080)
    assert en.diagnostics()["status"] == "operational"

def test_desktop_pack_valid():
    en = OmniVirtualDesktopSaaSArbiterEngine(1000, 1000)
    windows = [("a", 500, 500), ("b", 500, 500), ("c", 500, 500), ("d", 500, 500)]
    res = en.pack_virtual_windows(windows)
    assert res.is_ok()
    assert len(res.unwrap()["allocations"]) == 4

def test_desktop_pack_exceeds():
    en = OmniVirtualDesktopSaaSArbiterEngine(1000, 1000)
    windows = [("a", 800, 800), ("b", 800, 800)]
    res = en.pack_virtual_windows(windows)
    assert not res.is_ok()

def test_desktop_invalid_dimensions():
    en = OmniVirtualDesktopSaaSArbiterEngine(1000, 1000)
    windows = [("a", -10, 500)]
    assert not en.pack_virtual_windows(windows).is_ok()

def test_desktop_empty():
    en = OmniVirtualDesktopSaaSArbiterEngine(1000, 1000)
    res = en.pack_virtual_windows([])
    assert res.is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniPortfolioStaticGenerationEngine
# ---------------------------------------------------------
def test_portfolio_diagnostics():
    en = OmniPortfolioStaticGenerationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_portfolio_template_valid():
    en = OmniPortfolioStaticGenerationEngine()
    ast = "Hello {{ name }}, welcome to {{ region }}!"
    payload = {"name": "OMNI", "region": "Earth"}
    assert en.inject_ast_template(ast, payload).unwrap() == "Hello OMNI, welcome to Earth!"

def test_portfolio_template_missing_key():
    en = OmniPortfolioStaticGenerationEngine()
    ast = "Hello {{ name }}"
    payload = {}
    assert not en.inject_ast_template(ast, payload).is_ok()

def test_portfolio_invalid_type():
    en = OmniPortfolioStaticGenerationEngine()
    assert not en.inject_ast_template(123, {}).is_ok()

def test_portfolio_ast_empty():
    en = OmniPortfolioStaticGenerationEngine()
    assert en.inject_ast_template("", {"a": "1"}).unwrap() == ""

# ---------------------------------------------------------
# ENGINE 3: OmniPrivacyAwareCyberThreatEngine
# ---------------------------------------------------------
def test_threat_diagnostics():
    en = OmniPrivacyAwareCyberThreatEngine()
    assert en.diagnostics()["status"] == "operational"

def test_threat_evaluate_valid():
    en = OmniPrivacyAwareCyberThreatEngine(deviation_threshold=1.5)
    data = [10.0, 10.5, 9.5, 10.2, 10.0, 100.0]
    res = en.evaluate_telemetry_variance(data)
    assert res.is_ok()
    assert len(res.unwrap()["anomalies"]) > 0

def test_threat_evaluate_empty():
    en = OmniPrivacyAwareCyberThreatEngine()
    assert not en.evaluate_telemetry_variance([]).is_ok()

def test_threat_flat_distribution():
    en = OmniPrivacyAwareCyberThreatEngine()
    # Flat data -> 0 variance
    res = en.evaluate_telemetry_variance([5.0, 5.0, 5.0, 5.0])
    assert res.is_ok()
    assert len(res.unwrap()["anomalies"]) == 0

def test_threat_insufficient_data():
    en = OmniPrivacyAwareCyberThreatEngine()
    assert not en.evaluate_telemetry_variance([1.0, 2.0]).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniAgileSprintPlannerEngine
# ---------------------------------------------------------
def test_sprint_diagnostics():
    en = OmniAgileSprintPlannerEngine(100)
    assert en.diagnostics()["status"] == "operational"

def test_sprint_optimal():
    en = OmniAgileSprintPlannerEngine(10)
    # name, effort, value
    tasks = [("A", 5, 10), ("B", 4, 4), ("C", 6, 12), ("D", 3, 5)]
    res = en.plan_optimal_sprint(tasks)
    assert res.is_ok()
    data = res.unwrap()
    assert data["total_effort"] <= 10
    # Best combo is B=4, C=6 for value 4+12=16. Or A=5, D=3 (8 effort, val 15). C=6, D=3 (9 effort, val 17!)
    assert data["total_value"] == 17

def test_sprint_too_large():
    en = OmniAgileSprintPlannerEngine(2)
    tasks = [("A", 5, 10)]
    res = en.plan_optimal_sprint(tasks)
    assert res.unwrap()["total_value"] == 0

def test_sprint_negative_bounds():
    en = OmniAgileSprintPlannerEngine(10)
    assert not en.plan_optimal_sprint([("A", -1, 10)]).is_ok()

def test_sprint_empty():
    en = OmniAgileSprintPlannerEngine(10)
    assert not en.plan_optimal_sprint([]).is_ok()

# ---------------------------------------------------------
# ENGINE 5: OmniDeveloperRoadmapTraversalEngine
# ---------------------------------------------------------
def test_dag_diagnostics():
    en = OmniDeveloperRoadmapTraversalEngine()
    assert en.diagnostics()["status"] == "operational"

def test_dag_valid_traversal():
    en = OmniDeveloperRoadmapTraversalEngine()
    elements = ["A", "B", "C"]
    deps = [("A", "B"), ("A", "C"), ("B", "C")]
    res = en.traverse_curriculum_dag(elements, deps)
    assert res.is_ok()
    assert res.unwrap()["path"] == ["A", "B", "C"]

def test_dag_cyclical():
    en = OmniDeveloperRoadmapTraversalEngine()
    elements = ["A", "B"]
    deps = [("A", "B"), ("B", "A")]
    assert not en.traverse_curriculum_dag(elements, deps).is_ok()

def test_dag_missing_elements():
    en = OmniDeveloperRoadmapTraversalEngine()
    # Missing explicit definition
    elements = ["A"]
    deps = [("A", "B")]
    assert not en.traverse_curriculum_dag(elements, deps).is_ok()

def test_dag_empty():
    en = OmniDeveloperRoadmapTraversalEngine()
    assert not en.traverse_curriculum_dag([], []).is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniVideoEditorTimelineEngine
# ---------------------------------------------------------
def test_timeline_diagnostics():
    en = OmniVideoEditorTimelineEngine()
    assert en.diagnostics()["status"] == "operational"

def test_timeline_valid():
    en = OmniVideoEditorTimelineEngine()
    tracks = [(0, 0, 100), (1, 50, 150)] # Track 1 occludes track 0 from 50-100
    res = en.calculate_occluded_intervals(tracks)
    assert res.is_ok()
    data = res.unwrap()["visibility_matrix"]
    assert data[0]["visible_duration"] == 50
    assert data[1]["visible_duration"] == 100

def test_timeline_completely_eclipsed():
    en = OmniVideoEditorTimelineEngine()
    tracks = [(0, 10, 20), (1, 5, 25)]
    res = en.calculate_occluded_intervals(tracks)
    assert res.is_ok()
    data = res.unwrap()["visibility_matrix"]
    assert data[0]["is_completely_eclipsed"] is True

def test_timeline_invalid_duration():
    en = OmniVideoEditorTimelineEngine()
    assert not en.calculate_occluded_intervals([(0, 50, 10)]).is_ok()

def test_timeline_empty():
    en = OmniVideoEditorTimelineEngine()
    assert not en.calculate_occluded_intervals([]).is_ok()

# ---------------------------------------------------------
# ENGINE 7: OmniPythonProjectCategorizationEngine
# ---------------------------------------------------------
def test_jaccard_diagnostics():
    en = OmniPythonProjectCategorizationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_jaccard_clustering():
    en = OmniPythonProjectCategorizationEngine(jaccard_threshold=0.5)
    projects = [("A", ["web", "api", "flask"]), ("B", ["web", "api", "django"]), ("C", ["ml", "tensor", "gpu"])]
    res = en.dynamically_cluster_projects(projects)
    assert res.is_ok()
    data = res.unwrap()
    assert data["total_clusters"] == 2

def test_jaccard_empty_tags():
    en = OmniPythonProjectCategorizationEngine()
    projects = [("A", [])]
    assert not en.dynamically_cluster_projects(projects).is_ok()

def test_jaccard_no_overlap():
    en = OmniPythonProjectCategorizationEngine(jaccard_threshold=0.1)
    projects = [("A", ["a"]), ("B", ["b"]), ("C", ["c"])]
    res = en.dynamically_cluster_projects(projects)
    assert res.unwrap()["total_clusters"] == 3

def test_jaccard_empty_input():
    en = OmniPythonProjectCategorizationEngine()
    assert not en.dynamically_cluster_projects([]).is_ok()

# ---------------------------------------------------------
# ENGINE 8: OmniWhatsAppCommunicationBridgeEngine
# ---------------------------------------------------------
def test_whatsapp_diagnostics():
    en = OmniWhatsAppCommunicationBridgeEngine()
    assert en.diagnostics()["status"] == "operational"

def test_whatsapp_transmit():
    en = OmniWhatsAppCommunicationBridgeEngine()
    res = en.transmit_message_block([b"hello", b"world"])
    assert res.is_ok()
    assert res.unwrap()["transmitted"] == 2
    assert res.unwrap()["window"][0]["seq"] == 0

def test_whatsapp_acks():
    en = OmniWhatsAppCommunicationBridgeEngine(window_size=3)
    en.transmit_message_block([b"a", b"b", b"c"]) # Seqs: 0, 1, 2
    res = en.process_acknowledgement_window([0, 2])
    assert res.is_ok()
    assert res.unwrap()["dropped_seqs"] == [1]

def test_whatsapp_transmit_empty():
    en = OmniWhatsAppCommunicationBridgeEngine()
    assert not en.transmit_message_block([]).is_ok()

def test_whatsapp_perfect_acks():
    en = OmniWhatsAppCommunicationBridgeEngine(window_size=2)
    en.transmit_message_block([b"a", b"b"])
    res = en.process_acknowledgement_window([0, 1])
    assert res.unwrap()["is_stable"] is True

# ---------------------------------------------------------
# ENGINE 9: OmniGodotEntitySimulationEngine
# ---------------------------------------------------------
def test_godot_diagnostics():
    en = OmniGodotEntitySimulationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_godot_valid_hit():
    en = OmniGodotEntitySimulationEngine()
    atk = {"attack": 100.0, "armor": 10.0, "crit_chance": 0.0, "range": 5.0}
    dfnd = {"attack": 50.0, "armor": 100.0, "crit_chance": 0.0, "range": 2.0}
    res = en.resolve_kinematic_combat_exchange(atk, dfnd, 3.0)
    assert res.is_ok()
    data = res.unwrap()
    assert data["exchange_state"] == "hit"
    assert data["damage_inflicted"] == 50.0 # 100 * (100/(100+100)) = 50

def test_godot_out_of_range():
    en = OmniGodotEntitySimulationEngine()
    atk = {"attack": 100.0, "armor": 10.0, "crit_chance": 0.0, "range": 5.0}
    dfnd = {"attack": 50.0, "armor": 100.0, "crit_chance": 0.0, "range": 2.0}
    res = en.resolve_kinematic_combat_exchange(atk, dfnd, 6.0)
    assert res.unwrap()["exchange_state"] == "miss"

def test_godot_invalid_bounds():
    en = OmniGodotEntitySimulationEngine()
    atk = {"attack": 100.0}
    assert not en.resolve_kinematic_combat_exchange(atk, atk, 0.0).is_ok()

def test_godot_critical_hit():
    en = OmniGodotEntitySimulationEngine(crit_multiplier=2.0)
    atk = {"attack": 100.0, "armor": 10.0, "crit_chance": 1.0, "range": 5.0} # 100% crit
    dfnd = {"attack": 50.0, "armor": 0.0, "crit_chance": 0.0, "range": 2.0}
    res = en.resolve_kinematic_combat_exchange(atk, dfnd, 3.0)
    assert res.unwrap()["damage_inflicted"] == 200.0
    assert res.unwrap()["critical_strike"] is True

# ---------------------------------------------------------
# ENGINE 10: OmniCS253SoftwareCourseMatrixEngine
# ---------------------------------------------------------
def test_cs253_diagnostics():
    en = OmniCS253SoftwareCourseMatrixEngine()
    assert en.diagnostics()["status"] == "operational"

def test_cs253_valid_matrix():
    en = OmniCS253SoftwareCourseMatrixEngine(curve_shift=0.0)
    scores = [40, 50, 60, 70, 80]
    res = en.calculate_distribution_percentiles(scores)
    assert res.is_ok()
    data = res.unwrap()
    assert data["mean"] == 60.0
    assert data["median"] == 60.0

def test_cs253_invalid_score():
    en = OmniCS253SoftwareCourseMatrixEngine()
    assert not en.calculate_distribution_percentiles([150.0]).is_ok()

def test_cs253_empty_matrix():
    en = OmniCS253SoftwareCourseMatrixEngine()
    assert not en.calculate_distribution_percentiles([]).is_ok()

def test_cs253_curve_shift():
    en = OmniCS253SoftwareCourseMatrixEngine(curve_shift=10.0)
    scores = [40, 50, 60, 70, 80]
    res = en.calculate_distribution_percentiles(scores)
    # Mean is 60 without shift
    # With shift 10, A is > 60 + 15.8 = 75. But shifted values: [50, 60, 70, 80, 90]
    # mean_val = 60
    # std_dev ~ 15.8
    # Shifted bounds! 
    assert res.is_ok()
    assert res.unwrap()["mean"] == 60.0 # native mean unchanged
    assert res.unwrap()["distribution_matrix"]["A"] >= 1
