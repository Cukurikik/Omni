import pytest
import math
from src.compute.python_core.omni_markdown_ast_engine import OmniMarkdownAstEngine
from src.compute.python_core.omni_state_space_search_engine import OmniStateSpaceSearchEngine
from src.compute.python_core.omni_semantic_naming_engine import OmniSemanticNamingEngine
from src.compute.python_core.omni_cocomo_estimation_engine import OmniCocomoEstimationEngine
from src.compute.python_core.omni_recursive_backtracking_engine import OmniRecursiveBacktrackingEngine
from src.compute.python_core.omni_bitwise_memory_engine import OmniBitwiseMemoryEngine
from src.compute.python_core.omni_behavioral_patterns_engine import OmniBehavioralPatternsEngine
from src.compute.python_core.omni_fluid_dynamics_velocity_engine import OmniFluidDynamicsVelocityEngine
from src.compute.python_core.omni_token_bucket_throttle_engine import OmniTokenBucketThrottleEngine
from src.compute.python_core.omni_actor_concurrency_machine_engine import OmniActorConcurrencyMachineEngine
from src.compute.python_core.omni_base_engine import Ok, Err

# ---------------------------------------------------------
# 1. OmniMarkdownAstEngine Tests
# ---------------------------------------------------------
def test_markdown_ast_diagnostics():
    en = OmniMarkdownAstEngine()
    assert en.diagnostics()["status"] == "operational"

def test_markdown_ast_valid_parse():
    en = OmniMarkdownAstEngine()
    res = en.parse_headers_to_ast(["# Title", "## Subtitle", "body text"])
    assert res.is_ok()
    assert len(res.value["children"]) == 2
    assert res.value["children"][1]["level"] == 2
    assert res.value["children"][1]["content"] == "Subtitle"

def test_markdown_ast_invalid_parse():
    en = OmniMarkdownAstEngine()
    res = en.parse_headers_to_ast("Not A List")
    assert not res.is_ok()

def test_markdown_ast_depth_cap():
    en = OmniMarkdownAstEngine()
    res = en.parse_headers_to_ast(["######## Overlimit"])
    assert res.is_ok()
    assert res.value["children"][0]["level"] == 6
    assert res.value["children"][0]["content"] == "## Overlimit"

def test_markdown_ast_density():
    en = OmniMarkdownAstEngine()
    ast = {"type": "root", "children": [{"content": "abc"}, {"content": "d"}]}
    res = en.measure_semantic_density(ast)
    assert res.is_ok()
    assert res.value == 2.0

# ---------------------------------------------------------
# 2. OmniStateSpaceSearchEngine Tests
# ---------------------------------------------------------
def test_statespace_diagnostics():
    en = OmniStateSpaceSearchEngine()
    assert en.diagnostics()["status"] == "operational"

def test_statespace_depth_zero():
    en = OmniStateSpaceSearchEngine()
    res = en.minimax_evaluation(5.0, 0, True, -math.inf, math.inf)
    assert res.is_ok()
    assert res.value == 5.0

def test_statespace_invalid_depth():
    en = OmniStateSpaceSearchEngine()
    assert not en.minimax_evaluation(5.0, -1, True, -math.inf, math.inf).is_ok()

def test_statespace_maximizing():
    en = OmniStateSpaceSearchEngine()
    res = en.minimax_evaluation(10.0, 1, True, -math.inf, math.inf)
    assert res.is_ok()
    assert res.value == 10.5

def test_statespace_minimizing():
    en = OmniStateSpaceSearchEngine()
    res = en.minimax_evaluation(10.0, 1, False, -math.inf, math.inf)
    assert res.is_ok()
    assert res.value == 9.5

# ---------------------------------------------------------
# 3. OmniSemanticNamingEngine Tests
# ---------------------------------------------------------
def test_semantic_naming_diagnostics():
    en = OmniSemanticNamingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_semantic_naming_valid():
    en = OmniSemanticNamingEngine()
    assert en.validate_repository_kebab_case("valid-repo-name").value is True

def test_semantic_naming_uppercase():
    en = OmniSemanticNamingEngine()
    assert en.validate_repository_kebab_case("Invalid-RepoName").value is False

def test_semantic_naming_double_hyphen():
    en = OmniSemanticNamingEngine()
    assert en.validate_repository_kebab_case("invalid--repo").value is False

def test_semantic_naming_ends_hyphen():
    en = OmniSemanticNamingEngine()
    assert en.validate_repository_kebab_case("invalid-repo-").value is False

def test_semantic_naming_empty():
    en = OmniSemanticNamingEngine()
    assert not en.validate_repository_kebab_case("").is_ok()

# ---------------------------------------------------------
# 4. OmniCocomoEstimationEngine Tests
# ---------------------------------------------------------
def test_cocomo_diagnostics():
    en = OmniCocomoEstimationEngine()
    assert en.diagnostics()["status"] == "operational"

def test_cocomo_valid_estimation():
    en = OmniCocomoEstimationEngine()
    res = en.estimate_project_bounds(10.0)
    assert res.is_ok()
    assert "time_development_months" in res.value
    assert res.value["effort_person_months"] > 0

def test_cocomo_invalid_bounds():
    en = OmniCocomoEstimationEngine()
    assert not en.estimate_project_bounds(-5.0).is_ok()

def test_cocomo_zero_kloc():
    en = OmniCocomoEstimationEngine()
    assert not en.estimate_project_bounds(0).is_ok()

# ---------------------------------------------------------
# 5. OmniRecursiveBacktrackingEngine Tests
# ---------------------------------------------------------
def test_nqueens_diagnostics():
    en = OmniRecursiveBacktrackingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_nqueens_4x4():
    en = OmniRecursiveBacktrackingEngine()
    res = en.execute_n_queens_math(4)
    assert res.is_ok()
    assert res.value == 2

def test_nqueens_8x8():
    en = OmniRecursiveBacktrackingEngine()
    res = en.execute_n_queens_math(8)
    assert res.is_ok()
    assert res.value == 92

def test_nqueens_invalid_bound_low():
    en = OmniRecursiveBacktrackingEngine()
    assert not en.execute_n_queens_math(0).is_ok()

def test_nqueens_invalid_bound_high():
    en = OmniRecursiveBacktrackingEngine()
    assert not en.execute_n_queens_math(13).is_ok()

# ---------------------------------------------------------
# 6. OmniBitwiseMemoryEngine Tests
# ---------------------------------------------------------
def test_bitwise_diagnostics():
    en = OmniBitwiseMemoryEngine()
    assert en.diagnostics()["status"] == "operational"

def test_bitwise_valid_crypt():
    en = OmniBitwiseMemoryEngine()
    res = en.cyclic_xor_encryption([10, 20, 255], 128)
    assert res.is_ok()
    assert len(res.value) == 3

def test_bitwise_invalid_key():
    en = OmniBitwiseMemoryEngine()
    assert not en.cyclic_xor_encryption([10, 20], 300).is_ok()

def test_bitwise_invalid_sequence():
    en = OmniBitwiseMemoryEngine()
    assert not en.cyclic_xor_encryption([], 128).is_ok()

def test_bitwise_invalid_node():
    en = OmniBitwiseMemoryEngine()
    assert not en.cyclic_xor_encryption([10, 256], 128).is_ok()

# ---------------------------------------------------------
# 7. OmniBehavioralPatternsEngine Tests
# ---------------------------------------------------------
def test_behavioral_diagnostics():
    en = OmniBehavioralPatternsEngine()
    assert en.diagnostics()["status"] == "operational"

def test_behavioral_valid_mapping():
    en = OmniBehavioralPatternsEngine()
    op1 = lambda s: s.upper()
    op2 = lambda s: s + "_ok"
    res = en.execute_event_emission("base", [op1, op2])
    assert res.is_ok()
    assert res.value == ["BASE", "base_ok"]

def test_behavioral_invalid_root():
    en = OmniBehavioralPatternsEngine()
    assert not en.execute_event_emission("", [lambda s: s]).is_ok()

def test_behavioral_crashing_observer():
    en = OmniBehavioralPatternsEngine()
    def crasher(s): raise RuntimeError("boom")
    assert not en.execute_event_emission("base", [crasher]).is_ok()

def test_behavioral_empty_observers():
    en = OmniBehavioralPatternsEngine()
    res = en.execute_event_emission("base", [])
    assert res.is_ok()
    assert res.value == []

# ---------------------------------------------------------
# 8. OmniFluidDynamicsVelocityEngine Tests
# ---------------------------------------------------------
def test_fluid_diagnostics():
    en = OmniFluidDynamicsVelocityEngine()
    assert en.diagnostics()["status"] == "operational"

def test_fluid_velocity_valid():
    en = OmniFluidDynamicsVelocityEngine()
    res = en.compute_terminal_velocity(1.0, 0.47)
    assert res.is_ok()
    assert res.value > 0

def test_fluid_velocity_invalid_radius():
    en = OmniFluidDynamicsVelocityEngine()
    assert not en.compute_terminal_velocity(0.0, 0.47).is_ok()

def test_fluid_velocity_invalid_drag():
    en = OmniFluidDynamicsVelocityEngine()
    assert not en.compute_terminal_velocity(1.0, -0.47).is_ok()

# ---------------------------------------------------------
# 9. OmniTokenBucketThrottleEngine Tests
# ---------------------------------------------------------
def test_throttle_diagnostics():
    en = OmniTokenBucketThrottleEngine(10, 2.0)
    assert en.diagnostics()["status"] == "operational"

def test_throttle_valid():
    en = OmniTokenBucketThrottleEngine(5, 1.0)
    res = en.evaluate_request_burst([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 10.0])
    assert res.is_ok()
    assert res.value["accepted"] == 6

def test_throttle_depletion():
    en = OmniTokenBucketThrottleEngine(2, 0.0)
    res = en.evaluate_request_burst([1.0, 1.1, 1.2])
    assert res.is_ok()
    assert res.value["accepted"] == 2
    assert res.value["rejected"] == 1

def test_throttle_invalid_monotonic_time():
    en = OmniTokenBucketThrottleEngine(5, 1.0)
    assert not en.evaluate_request_burst([5.0, 1.0]).is_ok()

def test_throttle_invalid_setup():
    en = OmniTokenBucketThrottleEngine(-5, 1.0)
    assert not en.evaluate_request_burst([1.0]).is_ok()

# ---------------------------------------------------------
# 10. OmniActorConcurrencyMachineEngine Tests
# ---------------------------------------------------------
def test_actor_diagnostics():
    en = OmniActorConcurrencyMachineEngine()
    assert en.diagnostics()["status"] == "operational"

def test_actor_process_valid():
    en = OmniActorConcurrencyMachineEngine()
    res = en.process_immutable_state_mailbox(10, [{"action": "ADD", "value": 5}, {"action": "MUL", "value": 2}])
    assert res.is_ok()
    assert res.value == 30

def test_actor_process_zero_division():
    en = OmniActorConcurrencyMachineEngine()
    res = en.process_immutable_state_mailbox(10, [{"action": "DIV", "value": 0}])
    assert not res.is_ok()

def test_actor_process_invalid_op():
    en = OmniActorConcurrencyMachineEngine()
    assert not en.process_immutable_state_mailbox(10, [{"action": "POW", "value": 2}]).is_ok()

def test_actor_process_empty_mailbox():
    en = OmniActorConcurrencyMachineEngine()
    res = en.process_immutable_state_mailbox(99, [])
    assert res.is_ok()
    assert res.value == 99
