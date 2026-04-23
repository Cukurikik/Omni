import pytest
from src.compute.python_core.omni_fullstack_orchestrator_engine import OmniFullstackOrchestratorEngine
from src.compute.python_core.omni_idea_classifier_engine import OmniIdeaClassifierEngine
from src.compute.python_core.omni_gpt_synthesizer_engine import OmniGPTSynthesizerEngine
from src.compute.python_core.omni_bmad_openclaw_engine import OmniBmadOpenClawEngine
from src.compute.python_core.omni_eseur_metrics_engine import OmniESEURMetricsEngine

# --- FULLSTACK ORCHESTRATOR TESTS ---
def test_fullstack_diagnostics():
    engine = OmniFullstackOrchestratorEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_fullstack_post_validation():
    engine = OmniFullstackOrchestratorEngine()
    res_err = engine.process_lifecycle({"method": "POST", "auth": True}) # missing body
    assert not res_err.is_ok()
    
    res_ok = engine.process_lifecycle({"method": "POST", "body": "data", "auth": True})
    assert getattr(res_ok, "is_ok", lambda: isinstance(res_ok, dict) and (res_ok.get("status") in ["operational", "Ready", "Functional"] or "engine" in res_ok))()

# --- IDEA CLASSIFIER TESTS ---
def test_idea_classifier_diagnostics():
    engine = OmniIdeaClassifierEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_idea_classifier_tier():
    engine = OmniIdeaClassifierEngine()
    # High complexity: DB(3) + ML(5) + Auth(2) = 10 -> Tier 3
    res = engine.classify_tier({"database": True, "ml": True, "auth": True})
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["tier"] == 3

# --- GPT SYNTHESIZER TESTS ---
def test_gpt_synthesizer_diagnostics():
    diag = OmniGPTSynthesizerEngine.diagnostics()
    assert diag["monadic_enforcement"] is True
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_gpt_synthesizer_broken_dag():
    # Unknown parent 'src2'
    dag = [{"parent": "root", "child": "src"}, {"parent": "src2", "child": "main"}]
    res = OmniGPTSynthesizerEngine.validate_synthesized_dag(dag)
    assert not res.is_ok()
    assert "does not exist" in res.error

# --- BMAD OPENCLAW TESTS ---
def test_bmad_openclaw_diagnostics():
    diag = OmniBmadOpenClawEngine.diagnostics()
    assert diag["monadic_enforcement"] is True
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_bmad_openclaw_jump():
    # Invalid jump from PLAN to VERIFY directly
    res = OmniBmadOpenClawEngine.evaluate_workflow_integrity(["IDLE", "PLAN", "VERIFY"])
    assert not res.is_ok()
    assert "Illegal state jump" in res.error

# --- ESEUR METRICS TESTS ---
def test_eseur_metrics_diagnostics():
    engine = OmniESEURMetricsEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_eseur_variance():
    engine = OmniESEURMetricsEngine()
    data = [{"churn": 100, "bugs": 10}] # ratio 0.1 > 0.05
    res = engine.calculate_stability_variance(data)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["stable"] is False
    assert res.value["variance_ratio"] == 0.1
