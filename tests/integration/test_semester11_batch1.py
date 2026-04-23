import pytest
import math
from src.compute.python_core.omni_arting_api_engine import OmniArtingApiEngine
from src.compute.python_core.omni_blood_spatter_vision_engine import OmniBloodSpatterVisionEngine
from src.compute.python_core.omni_silicon_agent_engine import OmniSiliconAgentEngine
from src.compute.python_core.omni_claude_autonomous_engine import OmniClaudeAutonomousEngine
from src.compute.python_core.omni_kylin_terminal_engine import OmniKylinTerminalEngine
from src.compute.python_core.omni_school_management_engine import OmniSchoolManagementEngine
from src.compute.python_core.omni_suomi_pervasive_engine import OmniSuomiPervasiveEngine
from src.compute.python_core.omni_sadd_architecture_engine import OmniSaddArchitectureEngine
from src.compute.python_core.omni_advanced_programming_engine import OmniAdvancedProgrammingEngine
from src.compute.python_core.omni_structural_patterns_engine import OmniStructuralPatternsEngine
from src.compute.python_core.omni_base_engine import Ok, Err

# --- OmniArtingApiEngine Tests ---
def test_arting_diagnostics():
    en = OmniArtingApiEngine()
    d = en.diagnostics()
    assert d["status"] == "operational"

def test_arting_transform_valid():
    en = OmniArtingApiEngine()
    res = en.transform_dalle_to_sd({"prompt": "A futuristic city", "size": "1024x1024"})
    assert res.is_ok()
    assert res.value["width"] == 1024

def test_arting_transform_invalid_dict():
    en = OmniArtingApiEngine()
    res = en.transform_dalle_to_sd(["prompt: a city"])
    assert not res.is_ok()

def test_arting_constraints_valid():
    en = OmniArtingApiEngine()
    res = en.extract_bounding_constraints([{"x": 10, "y": 20, "mass": 2}])
    assert res.is_ok()
    assert res.value[0][2] == 19.62

def test_arting_constraints_invalid_mass():
    en = OmniArtingApiEngine()
    res = en.extract_bounding_constraints([{"x": 10, "y": 20, "mass": -1}])
    assert not res.is_ok()

# --- OmniBloodSpatterVisionEngine Tests ---
def test_blood_diagnostics():
    en = OmniBloodSpatterVisionEngine()
    d = en.diagnostics()
    assert d["domain"] == "3D Spatial Trigonometry"

def test_blood_impact_valid():
    en = OmniBloodSpatterVisionEngine()
    res = en.calculate_impact_angle(5.0, 10.0)
    assert res.is_ok()
    assert abs(res.value - 30.0) < 0.1

def test_blood_impact_invalid():
    en = OmniBloodSpatterVisionEngine()
    res = en.calculate_impact_angle(15.0, 10.0)
    assert not res.is_ok()

def test_blood_convergence_valid():
    en = OmniBloodSpatterVisionEngine()
    nodes = [
        {"x": 10, "y": 10, "width": 5, "length": 10, "distance_to_convergence": 20},
        {"x": -10, "y": 10, "width": 5, "length": 10, "distance_to_convergence": 20}
    ]
    res = en.compute_area_of_origin(nodes)
    assert res.is_ok()
    assert res.value["x_convergence"] == 0.0

def test_blood_convergence_invalid():
    en = OmniBloodSpatterVisionEngine()
    res = en.compute_area_of_origin([])
    assert not res.is_ok()

# --- OmniSiliconAgentEngine Tests ---
def test_silicon_diagnostics():
    en = OmniSiliconAgentEngine()
    d = en.diagnostics()
    assert d["status"] == "operational"

def test_silicon_register():
    en = OmniSiliconAgentEngine()
    res = en.register_agent("AgentA", "Builder", 2.0, 4.0)
    assert res.is_ok()

def test_silicon_register_invalid():
    en = OmniSiliconAgentEngine()
    res = en.register_agent("AgentB", "Builder", -1.0, 4.0)
    assert not res.is_ok()

def test_silicon_dag_cycle():
    en = OmniSiliconAgentEngine()
    en.register_agent("A", "Worker", 1.0, 1.0)
    en.register_agent("B", "Worker", 1.0, 1.0)
    en.attach_communication_edge("A", "B")
    res = en.attach_communication_edge("B", "A")
    assert not res.is_ok()

def test_silicon_overhead():
    en = OmniSiliconAgentEngine()
    en.register_agent("A", "Worker", 2.0, 1.0)
    en.register_agent("B", "Worker", 1.0, 3.0)
    res = en.compute_system_overhead()
    assert res.is_ok()
    assert res.value["total_cpu_cores"] == 3.0

# --- OmniClaudeAutonomousEngine Tests ---
def test_claude_diagnostics():
    en = OmniClaudeAutonomousEngine([[1.0]], ["T1"])
    d = en.diagnostics()
    assert d["status"] == "operational"

def test_claude_matrix_valid():
    mat = [[0.8, 0.2], [0.1, 0.9]]
    en = OmniClaudeAutonomousEngine(mat, ["T1", "T2"])
    assert en.validate_stochastic_matrix().is_ok()

def test_claude_matrix_invalid():
    mat = [[0.8, 0.3], [0.1, 0.9]]
    en = OmniClaudeAutonomousEngine(mat, ["T1", "T2"])
    assert not en.validate_stochastic_matrix().is_ok()

def test_claude_n_step():
    mat = [[0.0, 1.0], [1.0, 0.0]]
    en = OmniClaudeAutonomousEngine(mat, ["T1", "T2"])
    res = en.calculate_n_step_transition(0, 5) # Oscillates
    assert res.is_ok()
    assert res.value[1] == 1.0

def test_claude_n_step_bounds():
    mat = [[1.0]]
    en = OmniClaudeAutonomousEngine(mat, ["T1"])
    assert not en.calculate_n_step_transition(5, 1).is_ok()

# --- OmniKylinTerminalEngine Tests ---
def test_kylin_diagnostics():
    en = OmniKylinTerminalEngine()
    assert en.diagnostics()["status"] == "operational"

def test_kylin_injection():
    en = OmniKylinTerminalEngine()
    res = en.inject_node(-1, "rootscript", "base")
    assert res.is_ok()
    assert res.value == 1

def test_kylin_injection_invalid_script():
    en = OmniKylinTerminalEngine()
    res = en.inject_node(-1, "bad script name!", "base")
    assert not res.is_ok()

def test_kylin_hierarchy():
    en = OmniKylinTerminalEngine()
    r = en.inject_node(-1, "root", "root")
    c1 = en.inject_node(r.value, "childa", "a")
    c2 = en.inject_node(r.value, "childb", "b")
    res = en.resolve_hierarchy(r.value)
    assert res.is_ok()
    assert res.value == [r.value, c1.value, c2.value]

def test_kylin_hierarchy_invalid():
    en = OmniKylinTerminalEngine()
    assert not en.resolve_hierarchy(99).is_ok()

# --- OmniSchoolManagementEngine Tests ---
def test_school_diagnostics():
    en = OmniSchoolManagementEngine()
    assert en.diagnostics()["status"] == "operational"

def test_school_allocation():
    en = OmniSchoolManagementEngine()
    inst = ["T1", "T2"]
    crs = ["Math", "Sci"]
    mat = [[1, 0], [0, 1]]
    res = en.solve_resource_allocation(inst, crs, mat)
    assert res.is_ok()
    assert res.value["Math"] == "T1"

def test_school_allocation_complex():
    en = OmniSchoolManagementEngine()
    inst = ["T1", "T2"]
    crs = ["Math", "Sci"]
    mat = [[1, 1], [1, 0]]
    res = en.solve_resource_allocation(inst, crs, mat)
    assert res.is_ok()
    assert res.value["Math"] == "T2"

def test_school_allocation_invalid():
    en = OmniSchoolManagementEngine()
    inst = ["T1"]
    crs = ["Math", "Sci"]
    mat = [[1]] # Wrong dims
    assert not en.solve_resource_allocation(inst, crs, mat).is_ok()

def test_school_allocation_no_match():
    en = OmniSchoolManagementEngine()
    inst = ["T1"]
    crs = ["Math"]
    mat = [[0]]
    res = en.solve_resource_allocation(inst, crs, mat)
    assert res.is_ok()
    assert len(res.value) == 0

# --- OmniSuomiPervasiveEngine Tests ---
def test_suomi_diagnostics():
    en = OmniSuomiPervasiveEngine()
    assert en.diagnostics()["status"] == "operational"

def test_suomi_ema():
    en = OmniSuomiPervasiveEngine(0.5)
    res = en.calculate_ema_anomalies([10, 10, 10, 50], 10.0)
    assert res.is_ok()
    assert len(res.value) == 1

def test_suomi_ema_invalid_alpha():
    en = OmniSuomiPervasiveEngine(-0.1)
    res = en.calculate_ema_anomalies([10, 10], 10.0)
    assert not res.is_ok()

def test_suomi_ema_empty():
    en = OmniSuomiPervasiveEngine()
    assert not en.calculate_ema_anomalies([], 10.0).is_ok()

def test_suomi_ema_no_anomalies():
    en = OmniSuomiPervasiveEngine(0.5)
    res = en.calculate_ema_anomalies([10, 11, 10, 12], 10.0)
    assert res.is_ok()
    assert len(res.value) == 0

# --- OmniSaddArchitectureEngine Tests ---
def test_sadd_diagnostics():
    en = OmniSaddArchitectureEngine()
    assert en.diagnostics()["status"] == "operational"

def test_sadd_coupling():
    en = OmniSaddArchitectureEngine()
    res = en.evaluate_structural_coupling(["A", "B"], [("A", "B")])
    assert res.is_ok()
    assert res.value["instability"]["A"] == 1.0
    assert res.value["instability"]["B"] == 0.0

def test_sadd_coupling_isolated():
    en = OmniSaddArchitectureEngine()
    res = en.evaluate_structural_coupling(["A"], [])
    assert res.is_ok()
    assert res.value["instability"]["A"] == 0.0

def test_sadd_coupling_invalid():
    en = OmniSaddArchitectureEngine()
    res = en.evaluate_structural_coupling(["A", "B"], [("A", "C")])
    assert not res.is_ok()

def test_sadd_coupling_empty():
    en = OmniSaddArchitectureEngine()
    assert not en.evaluate_structural_coupling([], []).is_ok()

# --- OmniAdvancedProgrammingEngine Tests ---
def test_adv_diagnostics():
    en = OmniAdvancedProgrammingEngine()
    assert en.diagnostics()["status"] == "operational"

def test_adv_bind():
    en = OmniAdvancedProgrammingEngine()
    def op1(x): return Ok(x + 1)
    def op2(x): return Ok(x * 2)
    res = en.bind_monadic_operations(5, [op1, op2])
    if not res.is_ok(): print("ERR MSG:", res.unwrap_err())
    assert res.is_ok()
    assert res.value == 12

def test_adv_bind_failure():
    en = OmniAdvancedProgrammingEngine()
    def op1(x): return Ok(x + 1)
    def op2(x): return Err(ValueError("err"))
    res = en.bind_monadic_operations(5, [op1, op2])
    assert not res.is_ok()

def test_adv_bind_empty():
    en = OmniAdvancedProgrammingEngine()
    assert not en.bind_monadic_operations(5, []).is_ok()

def test_adv_bind_identity():
    en = OmniAdvancedProgrammingEngine()
    def op1(x): return Ok(x)
    res = en.bind_monadic_operations(99, [op1])
    assert res.is_ok()
    assert res.value == 99

# --- OmniStructuralPatternsEngine Tests ---
def test_struct_diagnostics():
    en = OmniStructuralPatternsEngine()
    assert en.diagnostics()["status"] == "operational"

def test_struct_singleton_valid():
    en = OmniStructuralPatternsEngine()
    res = en.validate_singleton_constraints([1234, 1234, 1234])
    assert res.is_ok()
    assert res.value is True

def test_struct_singleton_invalid():
    en = OmniStructuralPatternsEngine()
    res = en.validate_singleton_constraints([1234, 5678])
    assert res.is_ok()
    assert res.value is False

def test_struct_composite_depth():
    en = OmniStructuralPatternsEngine()
    res = en.composite_tree_depth({1: [2, 3], 2: [4]}, 1)
    assert res.is_ok()
    assert res.value == 3

def test_struct_composite_invalid():
    en = OmniStructuralPatternsEngine()
    assert not en.composite_tree_depth({1: [2]}, 99).is_ok()

def test_struct_composite_flat():
    en = OmniStructuralPatternsEngine()
    res = en.composite_tree_depth({1: []}, 1)
    assert res.is_ok()
    assert res.value == 1
