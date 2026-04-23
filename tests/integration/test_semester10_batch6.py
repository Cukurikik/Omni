import pytest
from src.compute.python_core.omni_academic_curriculum_graph_engine import OmniAcademicCurriculumGraphEngine
from src.compute.python_core.omni_microservices_banking_engine import OmniMicroservicesBankingEngine
from src.compute.python_core.omni_dev_softskills_cognitive_engine import OmniDevSoftSkillsCognitiveEngine
from src.compute.python_core.omni_ide_capability_taxonomy_engine import OmniIDECapabilityTaxonomyEngine
from src.compute.python_core.omni_privacy_policy_generator_engine import OmniPrivacyPolicyGeneratorEngine

# --- ACADEMIC CURRICULUM GRAPH TESTS ---
def test_academic_diagnostics():
    engine = OmniAcademicCurriculumGraphEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_academic_eligibility():
    engine = OmniAcademicCurriculumGraphEngine()
    dag = {3: [1, 2]}
    res = engine.verify_course_eligibility(3, dag, {1})
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert not res.value["eligible"]
    assert 2 in res.value["missing_prerequisites"]

def test_academic_already_completed():
    engine = OmniAcademicCurriculumGraphEngine()
    res = engine.verify_course_eligibility(1, {1: []}, {1})
    assert not res.is_ok()

# --- MICROSERVICES BANKING TESTS ---
def test_banking_diagnostics():
    engine = OmniMicroservicesBankingEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_banking_tcc_success():
    engine = OmniMicroservicesBankingEngine()
    res = engine.execute_tcc_transfer("A", "B", 40, {"A": 50, "B": 10})
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["result_state"]["A"] == 10
    assert res.value["result_state"]["B"] == 50

def test_banking_insufficient_funds():
    engine = OmniMicroservicesBankingEngine()
    res = engine.execute_tcc_transfer("A", "B", 100, {"A": 50, "B": 10})
    assert not res.is_ok()

# --- SOFT SKILLS COGNITIVE TESTS ---
def test_softskills_diagnostics():
    engine = OmniDevSoftSkillsCognitiveEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_softskills_friction():
    engine = OmniDevSoftSkillsCognitiveEngine()
    # EQ: comm(10)*1.5 + emp(10)*1.2 + lead(10)*1.0 = 15 + 12 + 10 = 37.
    # Friction load 100 / 38 = ~2.63 > 1.0. Unstainable.
    res = engine.evaluate_team_equilibrium({"communication": 10, "empathy": 10, "leadership": 10}, 100)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["sustainable"] is False

# --- IDE TAXONOMY TESTS ---
def test_ide_taxonomy_diagnostics():
    engine = OmniIDECapabilityTaxonomyEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_ide_taxonomy_tiers():
    engine = OmniIDECapabilityTaxonomyEngine()
    # Tier 2
    res2 = engine.classify_ide_tier(["SYNTAX", "LSP"])
    assert res2.value["tier"] == 2
    # Tier 4
    res4 = engine.classify_ide_tier(["SYNTAX", "LSP", "DEBUG", "PROFILE", "AI"])
    assert res4.value["tier"] == 4

# --- PRIVACY POLICY TESTS ---
def test_privacy_diagnostics():
    engine = OmniPrivacyPolicyGeneratorEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_privacy_inference():
    engine = OmniPrivacyPolicyGeneratorEngine()
    res = engine.infer_compliance_requirements(["CONTACTS", "GPS"])
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["pii_risk_score"] == 15
    assert "GDPR" in res.value["clauses"]
    assert res.value["requires_strict_opt_in"] is True
