import pytest
from src.compute.python_core.omni_mern_portfolio_routing_engine import OmniMernPortfolioRoutingEngine
from src.compute.python_core.omni_feline_agent_recovery_engine import OmniFelineAgentRecoveryEngine
from src.compute.python_core.omni_specif_ai_sdlc_engine import OmniSpecifAiSdlcEngine
from src.compute.python_core.omni_sciware_numerical_engine import OmniSciwareNumericalEngine
from src.compute.python_core.omni_pyrustic_gui_metrics_engine import OmniPyrusticGuiMetricsEngine

# --- MERN PORTFOLIO ROUTING TESTS ---
def test_mern_routing_diagnostics():
    engine = OmniMernPortfolioRoutingEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_mern_routing_valid_path():
    engine = OmniMernPortfolioRoutingEngine()
    res = engine.resolve_route_path("/about", "GET")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["resolved_component"] == "COMPONENT_ABOUT"
    assert res.value["status_code"] == 200

def test_mern_routing_api_middleware():
    engine = OmniMernPortfolioRoutingEngine()
    res = engine.resolve_route_path("/api/health", "POST")
    assert not res.is_ok()

def test_mern_routing_not_found():
    engine = OmniMernPortfolioRoutingEngine()
    res = engine.resolve_route_path("/unknown", "GET")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["status_code"] == 404

# --- FELINE AGENT RECOVERY TESTS ---
def test_feline_agent_diagnostics():
    engine = OmniFelineAgentRecoveryEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_feline_agent_recovery_success():
    engine = OmniFelineAgentRecoveryEngine()
    tasks = [{"id": 101, "fail_initially": True}, {"id": 102, "fail_initially": False}]
    res = engine.execute_resilient_workflow(tasks, max_retries=1)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["recovery_count"] == 1
    assert "TASK_101_RECOVERED" in res.value["completed_tasks"]
    assert "TASK_102_SUCCESS" in res.value["completed_tasks"]

def test_feline_agent_recovery_fail():
    engine = OmniFelineAgentRecoveryEngine()
    tasks = [{"id": 999, "fail_initially": True}]
    res = engine.execute_resilient_workflow(tasks, max_retries=0)
    assert not res.is_ok()

# --- SPECIF AI SDLC TESTS ---
def test_specif_ai_diagnostics():
    engine = OmniSpecifAiSdlcEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_specif_ai_requirements_extraction():
    engine = OmniSpecifAiSdlcEngine()
    concept = "A fast and secure user management portal."
    res = engine.extract_requirements(concept)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    modules = res.value["modules"]
    assert "USER_MANAGEMENT_MODULE" in modules
    assert "HIGH_PERFORMANCE_NFR" in modules
    assert "SECURITY_COMPLIANCE_NFR" in modules
    assert res.value["estimated_complexity_points"] == 45

def test_specif_ai_vague_input():
    engine = OmniSpecifAiSdlcEngine()
    res = engine.extract_requirements("A simple app.")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["status"] == "VAGUE_REQUIREMENTS"

# --- SCIWARE NUMERICAL TESTS ---
def test_sciware_diagnostics():
    engine = OmniSciwareNumericalEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_sciware_normalization_valid():
    engine = OmniSciwareNumericalEngine()
    data = [5.0, 10.0, 15.0]
    res = engine.normalize_scientific_array(data)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["normalized_matrix"] == [0.0, 0.5, 1.0]

def test_sciware_normalization_zero_variance():
    engine = OmniSciwareNumericalEngine()
    res = engine.normalize_scientific_array([42.0, 42.0])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["normalized_matrix"] == [1.0, 1.0]

def test_sciware_normalization_invalid_type():
    engine = OmniSciwareNumericalEngine()
    res = engine.normalize_scientific_array([5.0, "10.0"])
    assert not res.is_ok()

# --- PYRUSTIC GUI TESTS ---
def test_pyrustic_gui_diagnostics():
    engine = OmniPyrusticGuiMetricsEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_pyrustic_gui_pubsub():
    engine = OmniPyrusticGuiMetricsEngine()
    engine.register_megawidget("RELOAD", "WIDGET_A")
    engine.register_megawidget("RELOAD", "WIDGET_B")
    
    res = engine.trigger_megawidget_event("RELOAD", {"force": True})
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["dispatched_to"] == 2
    assert "WIDGET_A" in res.value["target_megawidgets"]

def test_pyrustic_gui_duplicate_registration():
    engine = OmniPyrusticGuiMetricsEngine()
    engine.register_megawidget("PING", "WIDGET_X")
    res = engine.register_megawidget("PING", "WIDGET_X")
    assert not res.is_ok()
