import pytest
import math
from src.compute.python_core.omni_federated_learning_engine import OmniFederatedLearningEngine
from src.compute.python_core.omni_symmetric_desktop_mirror_engine import OmniSymmetricDesktopMirrorEngine
from src.compute.python_core.omni_career_path_traversal_engine import OmniCareerPathTraversalEngine
from src.compute.python_core.omni_telecom_rate_limiting_engine import OmniTelecomRateLimitingEngine
from src.compute.python_core.omni_kinematic_collision_engine import OmniKinematicCollisionEngine
from src.compute.python_core.omni_project_resource_scheduler_engine import OmniProjectResourceSchedulerEngine
from src.compute.python_core.omni_portfolio_display_heuristics_engine import OmniPortfolioDisplayHeuristicsEngine
from src.compute.python_core.omni_utility_command_parser_engine import OmniUtilityCommandParserEngine
from src.compute.python_core.omni_cloud_terraform_diff_engine import OmniCloudTerraformDiffEngine
from src.compute.python_core.omni_fitness_caloric_delta_engine import OmniFitnessCaloricDeltaEngine
from src.compute.python_core.omni_base_engine import Ok, Err

# ---------------------------------------------------------
# 1. OmniFederatedLearningEngine Tests
# ---------------------------------------------------------
def test_federated_diagnostics():
    en = OmniFederatedLearningEngine()
    assert en.diagnostics()["status"] == "operational"

def test_federated_valid_averaging():
    en = OmniFederatedLearningEngine()
    global_w = [1.0, 1.0]
    updates = [[0.8, 1.2], [0.9, 1.1]]
    sizes = [100, 100]
    res = en.federated_averaging(global_w, updates, sizes)
    assert res.is_ok()
    assert res.value == [0.85, 1.15]

def test_federated_invalid_global():
    en = OmniFederatedLearningEngine()
    assert not en.federated_averaging([], [[1.0]], [100]).is_ok()

def test_federated_mismatched_sizes():
    en = OmniFederatedLearningEngine()
    assert not en.federated_averaging([1.0], [[1.0]], [100, 200]).is_ok()

def test_federated_mismatched_weights():
    en = OmniFederatedLearningEngine()
    assert not en.federated_averaging([1.0, 1.0], [[1.0]], [100]).is_ok()

# ---------------------------------------------------------
# 2. OmniSymmetricDesktopMirrorEngine Tests
# ---------------------------------------------------------
def test_mirror_diagnostics():
    en = OmniSymmetricDesktopMirrorEngine(1920, 1080)
    assert en.diagnostics()["status"] == "operational"

def test_mirror_vertical_flip():
    en = OmniSymmetricDesktopMirrorEngine(1920, 1080)
    res = en.calculate_mirror_projection([{"x": 420.0, "y": 500.0}], "vertical")
    assert res.is_ok()
    assert res.value[0]["x"] == 1500.0

def test_mirror_horizontal_flip():
    en = OmniSymmetricDesktopMirrorEngine(1920, 1080)
    res = en.calculate_mirror_projection([{"x": 420.0, "y": 100.0}], "horizontal")
    assert res.is_ok()
    assert res.value[0]["y"] == 980.0

def test_mirror_invalid_bounds():
    en = OmniSymmetricDesktopMirrorEngine(1920, 1080)
    assert not en.calculate_mirror_projection([{"x": 2000.0, "y": 100.0}], "vertical").is_ok()

def test_mirror_invalid_axis():
    en = OmniSymmetricDesktopMirrorEngine(1920, 1080)
    assert not en.calculate_mirror_projection([{"x": 100.0, "y": 100.0}], "diagonal").is_ok()

# ---------------------------------------------------------
# 3. OmniCareerPathTraversalEngine Tests
# ---------------------------------------------------------
def test_career_diagnostics():
    en = OmniCareerPathTraversalEngine()
    assert en.diagnostics()["status"] == "operational"

def test_career_valid_traversal():
    en = OmniCareerPathTraversalEngine()
    graph = {
        "A": {"B": 1.0, "C": 4.0},
        "B": {"C": 2.0},
        "C": {}
    }
    res = en.find_shortest_skill_path(graph, "A", "C")
    assert res.is_ok()
    assert res.value["total_weight"] == 3.0
    assert res.value["path"] == ["A", "B", "C"]

def test_career_unreachable_node():
    en = OmniCareerPathTraversalEngine()
    graph = {"A": {}, "B": {}}
    res = en.find_shortest_skill_path(graph, "A", "B")
    assert res.is_ok()
    assert res.value["total_weight"] == math.inf

def test_career_invalid_endpoints():
    en = OmniCareerPathTraversalEngine()
    graph = {"A": {"B": 1}}
    assert not en.find_shortest_skill_path(graph, "A", "C").is_ok()

def test_career_negative_weight():
    en = OmniCareerPathTraversalEngine()
    graph = {"A": {"B": -1.0}, "B": {}}
    assert not en.find_shortest_skill_path(graph, "A", "B").is_ok()

# ---------------------------------------------------------
# 4. OmniTelecomRateLimitingEngine Tests
# ---------------------------------------------------------
def test_rate_diagnostics():
    en = OmniTelecomRateLimitingEngine(10.0, 1.0)
    assert en.diagnostics()["status"] == "operational"

def test_rate_valid_burst():
    en = OmniTelecomRateLimitingEngine(10.0, 1.0)
    res = en.process_telemetry_burst([
        {"time": 1.0, "size": 5.0},
        {"time": 2.0, "size": 6.0}
    ])
    assert res.is_ok()
    # At t=2.0, 1 is leaked. current_level was 5.0. 5-1 = 4. 4+6 = 10 <= 10. accepted.
    assert res.value["accepted"] == 2
    assert res.value["dropped"] == 0

def test_rate_dropped_message():
    en = OmniTelecomRateLimitingEngine(10.0, 1.0)
    res = en.process_telemetry_burst([
        {"time": 1.0, "size": 8.0},
        {"time": 1.5, "size": 5.0}
    ])
    assert res.is_ok()
    # leaked 0.5. current = 7.5. 7.5+5 = 12.5 > 10. dropped.
    assert res.value["accepted"] == 1
    assert res.value["dropped"] == 1

def test_rate_non_monotonic_time():
    en = OmniTelecomRateLimitingEngine(10.0, 1.0)
    assert not en.process_telemetry_burst([{"time": 2.0, "size": 1.0}, {"time": 1.0, "size": 1.0}]).is_ok()

def test_rate_invalid_size():
    en = OmniTelecomRateLimitingEngine(10.0, 1.0)
    assert not en.process_telemetry_burst([{"time": 1.0, "size": -5.0}]).is_ok()

# ---------------------------------------------------------
# 5. OmniKinematicCollisionEngine Tests
# ---------------------------------------------------------
def test_collision_diagnostics():
    en = OmniKinematicCollisionEngine()
    assert en.diagnostics()["status"] == "operational"

def test_collision_valid_intersection():
    en = OmniKinematicCollisionEngine()
    res = en.detect_aabb_intersections([
        {"x": 0, "y": 0, "w": 10, "h": 10},
        {"x": 5, "y": 5, "w": 10, "h": 10}
    ])
    assert res.is_ok()
    assert [0, 1] in res.value

def test_collision_no_intersection():
    en = OmniKinematicCollisionEngine()
    res = en.detect_aabb_intersections([
        {"x": 0, "y": 0, "w": 10, "h": 10},
        {"x": 20, "y": 20, "w": 10, "h": 10}
    ])
    assert res.is_ok()
    assert len(res.value) == 0

def test_collision_corrupt_bounds():
    en = OmniKinematicCollisionEngine()
    assert not en.detect_aabb_intersections([{"x": 0, "w": 10, "h": 10}]).is_ok()

def test_collision_negative_dimensions():
    en = OmniKinematicCollisionEngine()
    assert not en.detect_aabb_intersections([{"x": 0, "y": 0, "w": -10, "h": 10}]).is_ok()

# ---------------------------------------------------------
# 6. OmniProjectResourceSchedulerEngine Tests
# ---------------------------------------------------------
def test_scheduler_diagnostics():
    en = OmniProjectResourceSchedulerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_scheduler_valid_cpm():
    en = OmniProjectResourceSchedulerEngine()
    tasks = {
        "A": {"duration": 2.0, "dependencies": []},
        "B": {"duration": 3.0, "dependencies": ["A"]},
        "C": {"duration": 1.0, "dependencies": ["A"]},
        "D": {"duration": 2.0, "dependencies": ["B", "C"]}
    }
    res = en.compute_critical_path(tasks)
    assert res.is_ok()
    assert res.value["critical_path_latency"] == 7.0

def test_scheduler_cyclic_dependency():
    en = OmniProjectResourceSchedulerEngine()
    tasks = {
        "A": {"duration": 1.0, "dependencies": ["B"]},
        "B": {"duration": 1.0, "dependencies": ["A"]}
    }
    assert not en.compute_critical_path(tasks).is_ok()

def test_scheduler_missing_dependency():
    en = OmniProjectResourceSchedulerEngine()
    tasks = {"A": {"duration": 1.0, "dependencies": ["Z"]}}
    assert not en.compute_critical_path(tasks).is_ok()

def test_scheduler_negative_duration():
    en = OmniProjectResourceSchedulerEngine()
    tasks = {"A": {"duration": -1.0, "dependencies": []}}
    assert not en.compute_critical_path(tasks).is_ok()

# ---------------------------------------------------------
# 7. OmniPortfolioDisplayHeuristicsEngine Tests
# ---------------------------------------------------------
def test_kmeans_diagnostics():
    en = OmniPortfolioDisplayHeuristicsEngine()
    assert en.diagnostics()["status"] == "operational"

def test_kmeans_valid_clustering():
    en = OmniPortfolioDisplayHeuristicsEngine()
    res = en.cluster_display_assets([[1,1], [2,2], [10,10], [11,11]], k=2)
    assert res.is_ok()
    assert len(res.value["centroids"]) == 2

def test_kmeans_k_out_of_bounds():
    en = OmniPortfolioDisplayHeuristicsEngine()
    assert not en.cluster_display_assets([[1,1]], k=5).is_ok()

def test_kmeans_fractured_dimensions():
    en = OmniPortfolioDisplayHeuristicsEngine()
    assert not en.cluster_display_assets([[1,1], [1,1,1]], k=1).is_ok()

def test_kmeans_empty_assets():
    en = OmniPortfolioDisplayHeuristicsEngine()
    assert not en.cluster_display_assets([], k=1).is_ok()

# ---------------------------------------------------------
# 8. OmniUtilityCommandParserEngine Tests
# ---------------------------------------------------------
def test_parser_diagnostics():
    en = OmniUtilityCommandParserEngine()
    assert en.diagnostics()["status"] == "operational"

def test_parser_valid_args():
    en = OmniUtilityCommandParserEngine()
    res = en.parse_native_cli_argument_tree('--name=test -v "spaced arg" pos')
    assert res.is_ok()
    assert res.value["flags"]["name"] == "test"
    assert res.value["flags"]["v"] is True
    assert "spaced arg" in res.value["positional"]

def test_parser_unclosed_quotes():
    en = OmniUtilityCommandParserEngine()
    assert not en.parse_native_cli_argument_tree('--name="unclosed').is_ok()

def test_parser_invalid_type():
    en = OmniUtilityCommandParserEngine()
    assert not en.parse_native_cli_argument_tree(1234).is_ok()

def test_parser_empty_string():
    en = OmniUtilityCommandParserEngine()
    res = en.parse_native_cli_argument_tree("")
    assert res.is_ok()
    assert len(res.value["positional"]) == 0

# ---------------------------------------------------------
# 9. OmniCloudTerraformDiffEngine Tests
# ---------------------------------------------------------
def test_diff_diagnostics():
    en = OmniCloudTerraformDiffEngine()
    assert en.diagnostics()["status"] == "operational"

def test_diff_valid_delta():
    en = OmniCloudTerraformDiffEngine()
    old = {"a": 1, "b": {"c": 2}}
    new = {"a": 1, "d": 3, "b": {"c": 99}}
    res = en.derive_structural_tree_delta(old, new)
    assert res.is_ok()
    assert res.value["added"]["d"] == 3
    assert res.value["mutated"]["b.c"]["to"] == 99

def test_diff_valid_removed():
    en = OmniCloudTerraformDiffEngine()
    res = en.derive_structural_tree_delta({"a": 1}, {})
    assert res.is_ok()
    assert res.value["removed"]["a"] == 1

def test_diff_invalid_type():
    en = OmniCloudTerraformDiffEngine()
    assert not en.derive_structural_tree_delta([], {}).is_ok()

def test_diff_empty_states():
    en = OmniCloudTerraformDiffEngine()
    res = en.derive_structural_tree_delta({}, {})
    assert res.is_ok()
    assert not res.value["added"]

# ---------------------------------------------------------
# 10. OmniFitnessCaloricDeltaEngine Tests
# ---------------------------------------------------------
def test_fitness_diagnostics():
    en = OmniFitnessCaloricDeltaEngine()
    assert en.diagnostics()["status"] == "operational"

def test_fitness_valid_calculation():
    en = OmniFitnessCaloricDeltaEngine()
    # Male, 80kg, 180cm, 30 years -> BMR approx 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    res = en.calculate_metabolic_velocity(80.0, 180.0, 30, "male", 1.5)
    assert res.is_ok()
    assert res.value["basal_metabolic_rate"] == 1780.0
    assert res.value["total_daily_energy_expenditure"] == 2670.0

def test_fitness_invalid_weight():
    en = OmniFitnessCaloricDeltaEngine()
    assert not en.calculate_metabolic_velocity(-10.0, 180.0, 30, "male", 1.5).is_ok()

def test_fitness_invalid_multiplier():
    en = OmniFitnessCaloricDeltaEngine()
    assert not en.calculate_metabolic_velocity(80.0, 180.0, 30, "male", 9.5).is_ok()

def test_fitness_invalid_gender():
    en = OmniFitnessCaloricDeltaEngine()
    assert not en.calculate_metabolic_velocity(80.0, 180.0, 30, "alien", 1.5).is_ok()
