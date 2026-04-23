import pytest
from src.compute.python_core.omni_cognitive_book_parsing_engine import OmniCognitiveBookParsingEngine
from src.compute.python_core.omni_rental_layered_architecture_engine import OmniRentalLayeredArchitectureEngine
from src.compute.python_core.omni_agent_lts_memory_engine import OmniAgentLtsMemoryEngine
from src.compute.python_core.omni_aws_sdlc_orchestration_engine import OmniAwsSdlcOrchestrationEngine

# --- COGNITIVE BOOK PARSING TESTS ---
def test_cognitive_diagnostics():
    engine = OmniCognitiveBookParsingEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_cognitive_optimal_retention():
    engine = OmniCognitiveBookParsingEngine()
    res = engine.evaluate_reading_retention(200, 1.2, 10) # velocity 20, load 24 -> Optimal
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["retention_assessment"] == "OPTIMAL"

def test_cognitive_overload():
    engine = OmniCognitiveBookParsingEngine()
    res = engine.evaluate_reading_retention(1000, 2.0, 5) # velocity 200, load 400 -> Overload
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["retention_assessment"] == "DEFICIT_COGNITIVE_OVERLOAD"

# --- RENTAL LAYERED ARCHITECTURE TESTS ---
def test_rental_layered_diagnostics():
    engine = OmniRentalLayeredArchitectureEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_rental_clean_traversal():
    engine = OmniRentalLayeredArchitectureEngine()
    res = engine.traverse_layer_boundaries(["UI", "BUSINESS", "DATA_ACCESS"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["transaction_committed"] is True

def test_rental_breach_traversal():
    engine = OmniRentalLayeredArchitectureEngine()
    res = engine.traverse_layer_boundaries(["UI", "DATA_ACCESS", "BUSINESS"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["transaction_committed"] is False
    assert "LAYER_BREACH" in res.value["violation"]

# --- AGENT LTS MEMORY TESTS ---
def test_agent_memory_diagnostics():
    engine = OmniAgentLtsMemoryEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_agent_memory_culling():
    engine = OmniAgentLtsMemoryEngine()
    blocks = [{"id": 1, "size": 40}, {"id": 2, "size": 50}, {"id": 3, "size": 30}] # total 120
    res = engine.index_and_cull_memory(blocks, max_capacity=100)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["purged_items"] == 1 # 40 purged, 80 left
    assert res.value["final_capacity_used"] == 80
    assert res.value["is_within_limits"] is True

def test_agent_memory_amnesia():
    engine = OmniAgentLtsMemoryEngine()
    blocks = [{"id": 1, "size": 40}]
    res = engine.index_and_cull_memory(blocks, max_capacity=0)
    assert not res.is_ok()

# --- AWS SDLC ORCHESTRATION TESTS ---
def test_aws_sdlc_diagnostics():
    engine = OmniAwsSdlcOrchestrationEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_aws_sdlc_ready():
    engine = OmniAwsSdlcOrchestrationEngine()
    res = engine.evaluate_orchestration_readiness(["AI_CODE_REVIEW", "CUSTOM_STEP", "AI_SECURITY_SCAN", "HUMAN_APPROVAL"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["ready_for_deploy"] is True

def test_aws_sdlc_not_ready_missing_approval():
    engine = OmniAwsSdlcOrchestrationEngine()
    res = engine.evaluate_orchestration_readiness(["AI_CODE_REVIEW", "AI_SECURITY_SCAN"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["ready_for_deploy"] is False
