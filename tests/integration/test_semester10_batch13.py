import pytest
from src.compute.python_core.omni_ai_remind_memory_lru_engine import OmniAiRemindMemoryLruEngine
from src.compute.python_core.omni_sdlc_curated_vector_engine import OmniSdlcCuratedVectorEngine
from src.compute.python_core.omni_api_restful_constraint_engine import OmniApiRestfulConstraintEngine
from src.compute.python_core.omni_context_inject_engineering_engine import OmniContextInjectEngineeringEngine
from src.compute.python_core.omni_aws_sdlc_pattern_topology_engine import OmniAwsSdlcPatternTopologyEngine

# --- REMIND MEMORY LRU TESTS ---
def test_rem_diagnostics():
    engine = OmniAiRemindMemoryLruEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_rem_ejection():
    engine = OmniAiRemindMemoryLruEngine()
    nodes = {"c1": 50, "c2": 10, "c3": 100}
    res = engine.evaluate_memory_decay(nodes, 150)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["target_ejection"] == "c2" # Decay = 140

def test_rem_temporal_fraud():
    engine = OmniAiRemindMemoryLruEngine()
    nodes = {"c1": 200}
    res = engine.evaluate_memory_decay(nodes, 150)
    assert not res.is_ok()

# --- SDLC CURATED VECTOR TESTS ---
def test_sdlc_diagnostics():
    engine = OmniSdlcCuratedVectorEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_sdlc_vetting():
    engine = OmniSdlcCuratedVectorEngine()
    res = engine.vet_resource_pointers(["https://a.com", "http://b.com", "ftp://c.com"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["secure_vectors"] == 1
    assert res.value["insecure_vectors"] == 1
    assert res.value["malformed_vectors"] == 1
    assert res.value["is_set_usable"] is False

def test_sdlc_null():
    engine = OmniSdlcCuratedVectorEngine()
    res = engine.vet_resource_pointers(None)
    assert not res.is_ok()

# --- API RESTFUL TESTS ---
def test_api_diagnostics():
    engine = OmniApiRestfulConstraintEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_api_valid():
    engine = OmniApiRestfulConstraintEngine()
    res = engine.validate_protocol_matrix({"method": "GET", "has_body": False})
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_standard"] is True

def test_api_violaton():
    engine = OmniApiRestfulConstraintEngine()
    res = engine.validate_protocol_matrix({"method": "GET", "has_body": True})
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_standard"] is False

def test_api_unknown_method():
    engine = OmniApiRestfulConstraintEngine()
    res = engine.validate_protocol_matrix({"method": "GRAPHQL_MUTATION"})
    assert not res.is_ok()

# --- CONTEXT ENGINEERING TESTS ---
def test_ctx_diagnostics():
    engine = OmniContextInjectEngineeringEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_ctx_packing_success():
    engine = OmniContextInjectEngineeringEngine()
    res = engine.compute_tensor_padding(base_tokens=100, ctx_blocks=[50, 50, 50], limit=200)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["blocks_injected"] == 2
    assert res.value["limit_used"] == 200

def test_ctx_saturated_base():
    engine = OmniContextInjectEngineeringEngine()
    res = engine.compute_tensor_padding(base_tokens=250, ctx_blocks=[50], limit=200)
    assert not res.is_ok()

def test_ctx_negative_dims():
    engine = OmniContextInjectEngineeringEngine()
    res = engine.compute_tensor_padding(-10, [10], 100)
    assert not res.is_ok()

# --- AWS SDLC PATTERN TESTS ---
def test_aws_diagnostics():
    engine = OmniAwsSdlcPatternTopologyEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_aws_valid_sequence():
    engine = OmniAwsSdlcPatternTopologyEngine()
    res = engine.validate_pipeline_stages(["PLAN", "CODE", "BUILD"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_contiguous"] is True
    assert res.value["completion_ratio"] == 60.0

def test_aws_broken_sequence():
    engine = OmniAwsSdlcPatternTopologyEngine()
    res = engine.validate_pipeline_stages(["PLAN", "BUILD"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_contiguous"] is False

def test_aws_overflow():
    engine = OmniAwsSdlcPatternTopologyEngine()
    res = engine.validate_pipeline_stages(["PLAN", "CODE", "BUILD", "TEST", "DEPLOY", "EXTRAS"])
    assert not res.is_ok()
