import pytest
from src.compute.python_core.omni_platzi_curriculum_engine import OmniPlatziCurriculumEngine
from src.compute.python_core.omni_sdlc_resource_taxonomy_engine import OmniSdlcResourceTaxonomyEngine
from src.compute.python_core.omni_api_discovery_routing_engine import OmniApiDiscoveryRoutingEngine
from src.compute.python_core.omni_gemini_context_engineering_engine import OmniGeminiContextEngineeringEngine
from src.compute.python_core.omni_agentic_design_pattern_engine import OmniAgenticDesignPatternEngine

# --- PLATZI CURRICULUM TESTS ---
def test_platzi_diagnostics():
    engine = OmniPlatziCurriculumEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_platzi_valid_sequence():
    engine = OmniPlatziCurriculumEngine()
    res = engine.validate_progression(["PYTHON", "PANDAS", "MACHINE_LEARNING"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_valid_sequence"] is True

def test_platzi_invalid_sequence():
    engine = OmniPlatziCurriculumEngine()
    res = engine.validate_progression(["PANDAS", "PYTHON"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_valid_sequence"] is False

# --- SDLC TAXONOMY TESTS ---
def test_sdlc_taxonomy_diagnostics():
    engine = OmniSdlcResourceTaxonomyEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_sdlc_taxonomy_devops():
    engine = OmniSdlcResourceTaxonomyEngine()
    res = engine.classify_resource("Docker and Deploy Pipelines")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["category"] == "DEVOPS_INFRASTRUCTURE"

# --- API DISCOVERY TESTS ---
def test_api_discovery_diagnostics():
    engine = OmniApiDiscoveryRoutingEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_api_discovery_valid():
    engine = OmniApiDiscoveryRoutingEngine()
    res = engine.validate_endpoint_syntax("https://api.system.com/v2/orders", "GET")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_restful"] is True
    
def test_api_discovery_insecure():
    engine = OmniApiDiscoveryRoutingEngine()
    res = engine.validate_endpoint_syntax("http://api.system.com/v2/orders", "POST")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_restful"] is False

# --- GEMINI CONTEXT TESTS ---
def test_gemini_context_diagnostics():
    engine = OmniGeminiContextEngineeringEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_gemini_context_optimal():
    engine = OmniGeminiContextEngineeringEngine()
    res = engine.evaluate_context_ratio("Evaluate this.", "Data is here, more data.")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["entropy_stability"] == "OPTIMAL"

def test_gemini_context_unstable():
    engine = OmniGeminiContextEngineeringEngine()
    res = engine.evaluate_context_ratio("Evaluate this complex request now.", "data")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["entropy_stability"] == "UNSTABLE_HEURISTIC"

# --- AGENTIC PATTERN TESTS ---
def test_agentic_pattern_diagnostics():
    engine = OmniAgenticDesignPatternEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_agentic_pattern_react_valid():
    engine = OmniAgenticDesignPatternEngine()
    res = engine.assess_pattern("REACT_PATTERN", {"has_thought": True, "has_action": True, "has_observation": True})
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_pattern_valid"] is True

def test_agentic_pattern_react_invalid():
    engine = OmniAgenticDesignPatternEngine()
    res = engine.assess_pattern("REACT_PATTERN", {"has_thought": True, "has_action": False, "has_observation": True})
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_pattern_valid"] is False
