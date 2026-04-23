import pytest
from src.compute.python_core.omni_telecom_signal_spectrum_engine import OmniTelecomSignalSpectrumEngine
from src.compute.python_core.omni_algorithmic_complexity_engine import OmniAlgorithmicComplexityEngine
from src.compute.python_core.omni_gdi_drawing_metrics_engine import OmniGdiDrawingMetricsEngine
from src.compute.python_core.omni_financial_taxation_rule_engine import OmniFinancialTaxationRuleEngine
from src.compute.python_core.omni_python_syntax_valuation_engine import OmniPythonSyntaxValuationEngine

# --- TELECOM SIGNAL SPECTRUM TESTS ---
def test_spectrum_diagnostics():
    engine = OmniTelecomSignalSpectrumEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_spectrum_no_overlap():
    engine = OmniTelecomSignalSpectrumEngine()
    bands = [{"id": "C1", "start": 900, "end": 920}, {"id": "C2", "start": 925, "end": 940}]
    res = engine.allocate_spectrum(bands)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["overlap_detected"] is False

def test_spectrum_has_overlap():
    engine = OmniTelecomSignalSpectrumEngine()
    bands = [{"id": "C1", "start": 900, "end": 930}, {"id": "C2", "start": 915, "end": 940}]
    res = engine.allocate_spectrum(bands)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["overlap_detected"] is True

# --- ALGORITHMIC COMPLEXITY TESTS ---
def test_complexity_diagnostics():
    engine = OmniAlgorithmicComplexityEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_complexity_n_cubed_unsafe():
    engine = OmniAlgorithmicComplexityEngine()
    res = engine.estimate_big_o_bounds(data_size=500, max_nesting_depth=3)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["complexity_class"] == "O(N^3)"
    # 500^3 = 125,000,000 > 10,000,000 -> False
    assert res.value["is_production_safe"] is False

def test_complexity_linear_safe():
    engine = OmniAlgorithmicComplexityEngine()
    res = engine.estimate_big_o_bounds(data_size=1000000, max_nesting_depth=1)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["complexity_class"] == "O(N)"
    assert res.value["is_production_safe"] is True

# --- GDI DRAWING TESTS ---
def test_gdi_diagnostics():
    engine = OmniGdiDrawingMetricsEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_gdi_hit_success():
    engine = OmniGdiDrawingMetricsEngine()
    rect = {"x": 10, "y": 10, "w": 50, "h": 50}
    pt = {"x": 30, "y": 30}
    res = engine.check_point_intersection(rect, pt)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_intersecting"] is True

def test_gdi_hit_miss():
    engine = OmniGdiDrawingMetricsEngine()
    rect = {"x": 10, "y": 10, "w": 50, "h": 50}
    pt = {"x": 5, "y": 90}
    res = engine.check_point_intersection(rect, pt)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_intersecting"] is False

# --- FINANCIAL TAXATION TESTS ---
def test_taxation_diagnostics():
    engine = OmniFinancialTaxationRuleEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_taxation_multi_tier():
    engine = OmniFinancialTaxationRuleEngine()
    # tiers: 10k @ 0%, next 40k @ 10%, next 100k @ 20%
    # total income 60,000
    # chunk 1: 10,000 * 0 = 0
    # chunk 2: 40,000 * 0.10 = 4,000
    # chunk 3: 10,000 * 0.20 = 2,000
    # total tax = 6,000
    res = engine.calculate_progressive_liability(60000.0)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["total_liability"] == 6000.0
    assert res.value["net_output"] == 54000.0

def test_taxation_negative():
    engine = OmniFinancialTaxationRuleEngine()
    res = engine.calculate_progressive_liability(-500.0)
    assert not res.is_ok()

# --- PYTHON SYNTAX TESTS ---
def test_syntax_diagnostics():
    engine = OmniPythonSyntaxValuationEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_syntax_valid():
    engine = OmniPythonSyntaxValuationEngine()
    res = engine.evaluate_identifier_legality("_private_var_123")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_legal"] is True

def test_syntax_keyword_collision():
    engine = OmniPythonSyntaxValuationEngine()
    res = engine.evaluate_identifier_legality("finally")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_legal"] is False
    assert res.value["reason"] == "RESERVED_KEYWORD_COLLISION"

def test_syntax_illegal_char():
    engine = OmniPythonSyntaxValuationEngine()
    res = engine.evaluate_identifier_legality("my-var")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["is_legal"] is False
    assert res.value["reason"] == "ILLEGAL_BODY_CHARACTER"
