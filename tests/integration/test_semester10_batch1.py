import pytest
from src.compute.python_core.omni_agentless_engine import OmniAgentlessEngine
from src.compute.python_core.omni_system_design_engine import OmniSystemDesignEngine
from src.compute.python_core.omni_design_patterns_engine import OmniDesignPatternsEngine, TransactionStep
from src.compute.python_core.omni_evolutionary_arch_engine import OmniEvolutionaryArchEngine
from src.compute.python_core.omni_claude_command_engine import OmniClaudeCommandEngine

def test_agentless_engine_diagnostics():
    engine = OmniAgentlessEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.value["ast_ops"] == "Functional"

def test_agentless_engine_parsing():
    engine = OmniAgentlessEngine()
    code = "def sample_func():\n    pass\n"
    result = engine.analyze_functions(code)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert "sample_func" in result.value

def test_system_design_engine_diagnostics():
    engine = OmniSystemDesignEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.value["ring_test"] == "Passed"

def test_system_design_engine_orchestration():
    engine = OmniSystemDesignEngine()
    nodes = ["NodeX", "NodeY", "NodeZ"]
    requests = ["Req1", "Req2", "Req3", "Req4", "Req5"]
    result = engine.orchestrate_ring(nodes, requests)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert len(result.value.keys()) == 3
    assert sum(result.value.values()) == 5

def test_design_patterns_engine_diagnostics():
    engine = OmniDesignPatternsEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.value["saga_engine"] == "Functional"

def test_design_patterns_saga_rollback():
    engine = OmniDesignPatternsEngine()
    state = {"count": 0}
    
    def step1(s): s["count"] += 1
    def comp1(s): s["count"] -= 1
    def step2(s): s["count"] += 10
    def comp2(s): s["count"] -= 10
    def step3(s): raise ValueError("Fail step 3")
    def comp3(s): pass

    steps = [
        TransactionStep("S1", step1, comp1),
        TransactionStep("S2", step2, comp2),
        TransactionStep("S3", step3, comp3),
    ]

    result = engine.execute_saga(steps, state)
    # The error should be caught, and compensation run (S1 and S2 compensated).
    # Result should be Err.
    assert not result.is_ok()
    assert state["count"] == 0  # Should be rolled back to 0

def test_evolutionary_arch_engine_diagnostics():
    engine = OmniEvolutionaryArchEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.value["fitness_func"] == "Functional"

def test_evolutionary_arch_fitness():
    engine = OmniEvolutionaryArchEngine()
    result = engine.calculate_fitness_score(15.0, 50.0, 5)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.value["fitness_penalty"] == 30.0
    assert result.value["passing"] is True

def test_claude_command_engine_diagnostics():
    engine = OmniClaudeCommandEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.value["parser"] == "Functional"

def test_claude_command_parsing():
    engine = OmniClaudeCommandEngine()
    result = engine.parse_deterministic_command("omni build --release -v --target=cloud")
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.value["binary"] == "omni"
    assert "release" in result.value["flags"]
    assert "v" in result.value["flags"]
    assert result.value["kwargs"].get("target") == "cloud"
