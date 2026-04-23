import pytest
from src.compute.python_core.omni_alogic_analyzer_engine import OmniAlogicAnalyzerEngine
from src.compute.python_core.omni_next_mvp_iteration_engine import OmniNextMVPIterationEngine
from src.compute.python_core.omni_content_based_filtering_engine import OmniContentBasedFilteringEngine
from src.compute.python_core.omni_software_event_analyzer_engine import OmniSoftwareEventAnalyzerEngine
from src.compute.python_core.omni_backend_interview_scoring_engine import OmniBackendInterviewScoringEngine
from src.compute.python_core.omni_cse_projects_curation_engine import OmniCSEProjectsCurationEngine
from src.compute.python_core.omni_2048_ai_game_engine import Omni2048AIGameEngine
from src.compute.python_core.omni_terraform_azure_provision_engine import OmniTerraformAzureProvisionEngine
from src.compute.python_core.omni_lose_it_fitness_tracking_engine import OmniLoseItFitnessTrackingEngine
from src.compute.python_core.omni_cyber_federated_learning_engine import OmniCyberFederatedLearningEngine

# ---------------------------------------------------------
# ENGINE 1: OmniAlogicAnalyzerEngine
# ---------------------------------------------------------
def test_alogic_diagnostics():
    en = OmniAlogicAnalyzerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_alogic_frequency_computation():
    en = OmniAlogicAnalyzerEngine()
    stream = [0, 1, 0, 1, 0, 1, 0, 1]
    res = en.compute_waveform_frequency(stream, 100.0)
    assert res.is_ok()
    data = res.unwrap()
    assert data["duty_cycle_percent"] == 50.0
    assert data["metrics"]["transitions_detected"] == 7

def test_alogic_empty_stream():
    en = OmniAlogicAnalyzerEngine()
    assert not en.compute_waveform_frequency([], 100.0).is_ok()

def test_alogic_invalid_state():
    en = OmniAlogicAnalyzerEngine()
    stream = [0, 2, 0]
    assert not en.compute_waveform_frequency(stream, 100.0).is_ok()

def test_alogic_zero_hz():
    en = OmniAlogicAnalyzerEngine()
    assert not en.compute_waveform_frequency([1, 0], 0).is_ok()

# ---------------------------------------------------------
# ENGINE 2: OmniNextMVPIterationEngine
# ---------------------------------------------------------
def test_mvp_diagnostics():
    en = OmniNextMVPIterationEngine(80.0)
    assert en.diagnostics()["status"] == "operational"

def test_mvp_viable_sprint():
    en = OmniNextMVPIterationEngine(80.0)
    comps = [{"name": "Auth", "cost_hours": 20}, {"name": "UI", "cost_hours": 30}]
    res = en.compute_sprint_viability(comps)
    assert res.is_ok()
    data = res.unwrap()
    assert data["is_viable_single_sprint"] is True
    assert len(data["allocations"]["approved_components"]) == 2

def test_mvp_overflow_sprint():
    en = OmniNextMVPIterationEngine(80.0)
    comps = [{"name": "A", "cost_hours": 50}, {"name": "B", "cost_hours": 40}]
    res = en.compute_sprint_viability(comps)
    assert res.is_ok()
    data = res.unwrap()
    assert data["is_viable_single_sprint"] is False
    assert "A" in data["allocations"]["approved_components"]
    assert "B" in data["allocations"]["deferred_components"]

def test_mvp_empty_components():
    en = OmniNextMVPIterationEngine()
    assert not en.compute_sprint_viability([]).is_ok()

def test_mvp_zero_cost():
    en = OmniNextMVPIterationEngine()
    comps = [{"name": "Zero", "cost_hours": 0}]
    assert not en.compute_sprint_viability(comps).is_ok()

# ---------------------------------------------------------
# ENGINE 3: OmniContentBasedFilteringEngine
# ---------------------------------------------------------
def test_cbf_diagnostics():
    en = OmniContentBasedFilteringEngine()
    assert en.diagnostics()["status"] == "operational"

def test_cbf_similarity():
    en = OmniContentBasedFilteringEngine()
    target = [1.0, 0.0]
    refs = [{"id": "R1", "vector": [1.0, 0.0]}, {"id": "R2", "vector": [0.0, 1.0]}]
    res = en.compute_cosine_similarity_matrix(target, refs)
    assert res.is_ok()
    data = res.unwrap()
    assert data["ranked_outputs"][0]["id"] == "R1"
    assert data["ranked_outputs"][0]["similarity_score"] == 1.0
    assert data["ranked_outputs"][1]["similarity_score"] == 0.0

def test_cbf_dimension_mismatch():
    en = OmniContentBasedFilteringEngine()
    target = [1.0, 1.0]
    refs = [{"id": "R1", "vector": [1.0]}]
    assert not en.compute_cosine_similarity_matrix(target, refs).is_ok()

def test_cbf_zero_vector():
    en = OmniContentBasedFilteringEngine()
    # Null dimension mathematically
    assert not en.compute_cosine_similarity_matrix([0.0, 0.0], [{"id": "R1", "vector": [1.0, 1.0]}]).is_ok()

def test_cbf_empty_refs():
    en = OmniContentBasedFilteringEngine()
    assert not en.compute_cosine_similarity_matrix([1.0], []).is_ok()

# ---------------------------------------------------------
# ENGINE 4: OmniSoftwareEventAnalyzerEngine
# ---------------------------------------------------------
def test_event_diagnostics():
    en = OmniSoftwareEventAnalyzerEngine()
    assert en.diagnostics()["status"] == "operational"

def test_event_valid_trace():
    en = OmniSoftwareEventAnalyzerEngine(10.0)
    trace = [
        {"event_id": 1, "type": "function_enter", "duration_ms": 5.0},
        {"event_id": 2, "type": "function_exit", "duration_ms": 15.0} # Anomaly
    ]
    res = en.analyze_stack_trace_topology(trace)
    assert res.is_ok()
    data = res.unwrap()
    assert data["diagnostics_summary"]["max_call_stack_depth"] == 1
    assert data["diagnostics_summary"]["anomalous_events"] == 1
    assert data["anomalies"][0]["over_threshold_ms"] == 5.0

def test_event_empty_trace():
    en = OmniSoftwareEventAnalyzerEngine()
    assert not en.analyze_stack_trace_topology([]).is_ok()

def test_event_malformed_trace():
    en = OmniSoftwareEventAnalyzerEngine()
    assert not en.analyze_stack_trace_topology([{"unknown": 1}]).is_ok()

def test_event_stack_underflow():
    # Will just map to depth 0 natively
    en = OmniSoftwareEventAnalyzerEngine(10.0)
    trace = [{"event_id": 1, "type": "function_exit", "duration_ms": 5.0}]
    res = en.analyze_stack_trace_topology(trace)
    assert res.unwrap()["diagnostics_summary"]["max_call_stack_depth"] == 0

# ---------------------------------------------------------
# ENGINE 5: OmniBackendInterviewScoringEngine
# ---------------------------------------------------------
def test_scoring_diagnostics():
    en = OmniBackendInterviewScoringEngine()
    assert en.diagnostics()["status"] == "operational"

def test_scoring_strong():
    en = OmniBackendInterviewScoringEngine(["api", "database", "cache", "scalability"])
    ans = "We should use a database to ensure scalability and use a cache for the api."
    res = en.compute_heuristic_score(ans)
    assert res.is_ok()
    data = res.unwrap()
    assert data["evaluation_status"] == "STRONG"
    assert data["score_percentage"] == 100.0

def test_scoring_moderate():
    en = OmniBackendInterviewScoringEngine(["api", "database", "cache", "scalability"])
    ans = "Just cache the api calls."
    res = en.compute_heuristic_score(ans)
    assert res.is_ok()
    assert res.unwrap()["evaluation_status"] == "MODERATE"

def test_scoring_weak():
    en = OmniBackendInterviewScoringEngine(["api", "database", "cache"])
    ans = "idk man"
    res = en.compute_heuristic_score(ans)
    assert res.is_ok()
    assert res.unwrap()["evaluation_status"] == "WEAK"

def test_scoring_empty():
    en = OmniBackendInterviewScoringEngine()
    assert not en.compute_heuristic_score("").is_ok()

# ---------------------------------------------------------
# ENGINE 6: OmniCSEProjectsCurationEngine
# ---------------------------------------------------------
def test_curation_diagnostics():
    en = OmniCSEProjectsCurationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_curation_clustering():
    en = OmniCSEProjectsCurationEngine()
    projects = [
        {"name": "P1", "tags": ["db", "api"]},
        {"name": "P2", "tags": ["hack", "sec"]},
        {"name": "P3", "tags": ["unknown"]}
    ]
    domains = {
        "Backend": ["db", "api", "cache"],
        "Security": ["hack", "sec", "crypto"]
    }
    res = en.categorize_project_matrix(projects, domains)
    assert res.is_ok()
    data = res.unwrap()
    assert "P1" in data["clusters"]["Backend"]
    assert "P2" in data["clusters"]["Security"]
    assert "P3" in data["clusters"]["Uncategorized"]

def test_curation_empty_projects():
    en = OmniCSEProjectsCurationEngine()
    assert not en.categorize_project_matrix([], {"D": ["d"]}).is_ok()

def test_curation_malformed():
    en = OmniCSEProjectsCurationEngine()
    assert not en.categorize_project_matrix([{"invalid": 1}], {"D": ["d"]}).is_ok()

def test_curation_overlap():
    en = OmniCSEProjectsCurationEngine()
    projects = [{"name": "Both", "tags": ["db", "api", "hack"]}]
    domains = {"Backend": ["db", "api"], "Sec": ["hack"]}
    res = en.categorize_project_matrix(projects, domains)
    data = res.unwrap()
    assert "Both" in data["clusters"]["Backend"]

# ---------------------------------------------------------
# ENGINE 7: Omni2048AIGameEngine
# ---------------------------------------------------------
def test_2048_diagnostics():
    en = Omni2048AIGameEngine()
    assert en.diagnostics()["status"] == "operational"

def test_2048_shift_merge():
    en = Omni2048AIGameEngine(4)
    # [2, 2, 0, 4] -> [4, 4, 0, 0]
    res = en.shift_row_left([2, 2, 0, 4])
    assert res.is_ok()
    data = res.unwrap()
    assert data["shifted_matrix_vector"] == [4, 4, 0, 0]
    assert data["score_delta"] == 4

def test_2048_shift_no_merge():
    en = Omni2048AIGameEngine(4)
    res = en.shift_row_left([2, 4, 0, 8])
    assert res.unwrap()["shifted_matrix_vector"] == [2, 4, 8, 0]

def test_2048_invalid_dimension():
    en = Omni2048AIGameEngine(4)
    assert not en.shift_row_left([2, 2]).is_ok()

def test_2048_cascade_limit():
    en = Omni2048AIGameEngine(4)
    # native bounds prevents cascading in single turn. [2, 2, 2, 2] -> [4, 4, 0, 0]
    res = en.shift_row_left([2, 2, 2, 2])
    data = res.unwrap()
    assert data["shifted_matrix_vector"] == [4, 4, 0, 0]

# ---------------------------------------------------------
# ENGINE 8: OmniTerraformAzureProvisionEngine
# ---------------------------------------------------------
def test_terraform_diagnostics():
    en = OmniTerraformAzureProvisionEngine()
    assert en.diagnostics()["status"] == "operational"

def test_terraform_valid_dag():
    en = OmniTerraformAzureProvisionEngine()
    res = en.compute_topological_sort_deploy_sequence({
        "VNet": [],
        "Subnet": ["VNet"],
        "VM": ["Subnet"]
    })
    assert res.is_ok()
    data = res.unwrap()
    assert data["structured_execution_plan"] == ["VNet", "Subnet", "VM"]

def test_terraform_cycle():
    en = OmniTerraformAzureProvisionEngine()
    assert not en.compute_topological_sort_deploy_sequence({
        "A": ["B"],
        "B": ["A"]
    }).is_ok()

def test_terraform_undefined_dependency():
    en = OmniTerraformAzureProvisionEngine()
    assert not en.compute_topological_sort_deploy_sequence({
        "A": ["C"] # C not declared
    }).is_ok()

def test_terraform_empty():
    en = OmniTerraformAzureProvisionEngine()
    assert not en.compute_topological_sort_deploy_sequence({}).is_ok()

# ---------------------------------------------------------
# ENGINE 9: OmniLoseItFitnessTrackingEngine
# ---------------------------------------------------------
def test_fitness_diagnostics():
    en = OmniLoseItFitnessTrackingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_fitness_balance():
    en = OmniLoseItFitnessTrackingEngine(2000.0)
    intakes = [2500, 2000]
    expends = [200, 300]
    res = en.calculate_rolling_caloric_balance(intakes, expends)
    assert res.is_ok()
    data = res.unwrap()
    # Day 1: 2500 - (2000+200) = +300
    # Day 2: 2000 - (2000+300) = -300
    # Cumulative: 0
    assert data["rolling_deltas_matrix"] == [300.0, -300.0]
    assert data["cumulative_balance"] == 0.0
    assert data["trajectory"] == "MAINTENANCE"

def test_fitness_mismatch_arrays():
    en = OmniLoseItFitnessTrackingEngine()
    assert not en.calculate_rolling_caloric_balance([2000], []).is_ok()

def test_fitness_empty_arrays():
    en = OmniLoseItFitnessTrackingEngine()
    assert not en.calculate_rolling_caloric_balance([], []).is_ok()

def test_fitness_trajectory():
    en = OmniLoseItFitnessTrackingEngine(2000.0)
    res = en.calculate_rolling_caloric_balance([1500], [0])
    assert res.unwrap()["trajectory"] == "WEIGHT_LOSS"

# ---------------------------------------------------------
# ENGINE 10: OmniCyberFederatedLearningEngine
# ---------------------------------------------------------
def test_federated_diagnostics():
    en = OmniCyberFederatedLearningEngine()
    assert en.diagnostics()["status"] == "operational"

def test_federated_aggregation():
    en = OmniCyberFederatedLearningEngine(0.01)
    peers = [
        [0.4, 0.2],
        [0.6, 0.4]
    ]
    res = en.aggregate_global_gradients_federated(peers)
    assert res.is_ok()
    data = res.unwrap()
    # Mean of idx 0: 0.5. With noise: 0.51
    assert data["global_aggregated_weights"][0] == 0.51
    assert data["global_aggregated_weights"][1] == 0.31

def test_federated_mismatched_dimensions():
    en = OmniCyberFederatedLearningEngine()
    peers = [[0.4, 0.2], [0.6]]
    assert not en.aggregate_global_gradients_federated(peers).is_ok()

def test_federated_empty_peers():
    en = OmniCyberFederatedLearningEngine()
    assert not en.aggregate_global_gradients_federated([]).is_ok()

def test_federated_precision_rounding():
    en = OmniCyberFederatedLearningEngine(0.000001)
    peers = [[1.0], [0.0], [0.0]]
    res = en.aggregate_global_gradients_federated(peers)
    data = res.unwrap()
    # 0.333333 + 0.000001 = 0.333334
    assert data["global_aggregated_weights"][0] == 0.333334
