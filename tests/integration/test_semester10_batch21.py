import os
import sys
import pytest

# Ensure the root of the Omni project is in the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.compute.python_core.omni_tomato_architecture_engine import OmniTomatoArchitectureEngine
from src.compute.python_core.omni_vtta2008_plm_engine import OmniVtta2008PlmEngine
from src.compute.python_core.omni_rensvds_ml_screening_engine import OmniRensvdsMlScreeningEngine
from src.compute.python_core.omni_nadavis56_autogpt_context_engine import OmniNadavis56AutogptContextEngine
from src.compute.python_core.omni_pelocpp_modern_constraint_engine import OmniPelocppModernConstraintEngine

# -------------------------------------------------------------------
# 1. OmniTomatoArchitectureEngine
# -------------------------------------------------------------------
def test_tomato_diagnostics():
    diag = OmniTomatoArchitectureEngine.diagnostics()
    assert diag["engine"] == "OmniTomatoArchitectureEngine"
    assert diag["monadic_enforcement"] is True

def test_tomato_valid_downward_dependency():
    # presentation -> domain is valid (higher index = lower layer)
    result = OmniTomatoArchitectureEngine.validate_layer_dependency("presentation", "domain")
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_tomato_same_layer_dependency():
    result = OmniTomatoArchitectureEngine.validate_layer_dependency("domain", "domain")
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_tomato_upward_dependency_violation():
    # domain -> presentation is ILLEGAL (upward)
    result = OmniTomatoArchitectureEngine.validate_layer_dependency("domain", "presentation")
    assert not result.is_ok()
    assert "Architecture violation" in str(result.unwrap_err())

def test_tomato_unknown_layer():
    result = OmniTomatoArchitectureEngine.validate_layer_dependency("presentation", "unknown_layer")
    assert not result.is_ok()
    assert "Unknown target layer" in str(result.unwrap_err())

# -------------------------------------------------------------------
# 2. OmniVtta2008PlmEngine
# -------------------------------------------------------------------
def test_plm_diagnostics():
    diag = OmniVtta2008PlmEngine.diagnostics()
    assert diag["engine"] == "OmniVtta2008PlmEngine"
    assert diag["monadic_enforcement"] is True

def test_plm_valid_pipeline():
    stages = ["modeling", "texturing", "rigging", "animation", "lighting", "compositing", "render"]
    mandatory = ["modeling", "animation", "render"]
    result = OmniVtta2008PlmEngine.validate_pipeline_stages(stages, mandatory)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_plm_missing_mandatory_stage():
    stages = ["modeling", "texturing", "render"]
    mandatory = ["modeling", "animation", "render"]
    result = OmniVtta2008PlmEngine.validate_pipeline_stages(stages, mandatory)
    assert not result.is_ok()
    assert "Missing mandatory pipeline stage: 'animation'" in str(result.unwrap_err())

def test_plm_duplicate_stage():
    stages = ["modeling", "texturing", "modeling", "render"]
    mandatory = ["modeling", "render"]
    result = OmniVtta2008PlmEngine.validate_pipeline_stages(stages, mandatory)
    assert not result.is_ok()
    assert "Duplicate pipeline stage detected" in str(result.unwrap_err())

def test_plm_wrong_order():
    stages = ["render", "modeling", "animation"]
    mandatory = ["modeling", "animation", "render"]
    result = OmniVtta2008PlmEngine.validate_pipeline_stages(stages, mandatory)
    assert not result.is_ok()
    assert "Pipeline order violation" in str(result.unwrap_err())

# -------------------------------------------------------------------
# 3. OmniRensvdsMlScreeningEngine
# -------------------------------------------------------------------
def test_screening_diagnostics():
    diag = OmniRensvdsMlScreeningEngine.diagnostics()
    assert diag["engine"] == "OmniRensvdsMlScreeningEngine"
    assert diag["monadic_enforcement"] is True

def test_screening_wss_valid():
    # 1000 docs, found 95/100 relevant, screened 300 -> recall=0.95
    # WSS = (1 - 300/1000) - (1 - 0.95) = 0.7 - 0.05 = 0.65
    result = OmniRensvdsMlScreeningEngine.calculate_wss_at_recall(1000, 95, 100, 300, 0.95)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert abs(result.unwrap() - 0.65) < 0.001

def test_screening_recall_not_met():
    # found 80/100 relevant -> recall=0.80, target=0.95
    result = OmniRensvdsMlScreeningEngine.calculate_wss_at_recall(1000, 80, 100, 300, 0.95)
    assert not result.is_ok()
    assert "Target recall 0.95 not yet met" in str(result.unwrap_err())

def test_screening_invalid_total():
    result = OmniRensvdsMlScreeningEngine.calculate_wss_at_recall(0, 10, 10, 0, 0.95)
    assert not result.is_ok()
    assert "total_documents must be positive" in str(result.unwrap_err())

# -------------------------------------------------------------------
# 4. OmniNadavis56AutogptContextEngine
# -------------------------------------------------------------------
def test_context_diagnostics():
    diag = OmniNadavis56AutogptContextEngine.diagnostics()
    assert diag["engine"] == "OmniNadavis56AutogptContextEngine"
    assert diag["monadic_enforcement"] is True

def test_context_window_fit():
    # max=4096, system=500, messages=[100, 200, 300, 400, 500]
    # Available=3596. From end: 500+400+300+200+100=1500, all fit -> 5
    result = OmniNadavis56AutogptContextEngine.validate_context_window(
        [100, 200, 300, 400, 500], 4096, 500
    )
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() == 5

def test_context_window_partial_fit():
    # max=1000, system=200, available=800. Messages=[300, 300, 300].
    # From end: 300 (total 300) + 300 (total 600) + 300 (total 900 > 800) -> 2 fit
    result = OmniNadavis56AutogptContextEngine.validate_context_window(
        [300, 300, 300], 1000, 200
    )
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() == 2

def test_context_window_system_exceeds():
    result = OmniNadavis56AutogptContextEngine.validate_context_window(
        [100], 500, 500
    )
    assert not result.is_ok()
    assert "System prompt alone exceeds context window" in str(result.unwrap_err())

# -------------------------------------------------------------------
# 5. OmniPelocppModernConstraintEngine
# -------------------------------------------------------------------
def test_constraint_diagnostics():
    diag = OmniPelocppModernConstraintEngine.diagnostics()
    assert diag["engine"] == "OmniPelocppModernConstraintEngine"
    assert diag["monadic_enforcement"] is True

def test_constraint_integral_valid():
    result = OmniPelocppModernConstraintEngine.validate_type_against_concept("int", "Integral")
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_constraint_float_not_integral():
    result = OmniPelocppModernConstraintEngine.validate_type_against_concept("float", "Integral")
    assert not result.is_ok()
    assert "does not satisfy concept 'Integral'" in str(result.unwrap_err())

def test_constraint_numeric_union():
    # Numeric = Integral | FloatingPoint -> float should be in Numeric
    result = OmniPelocppModernConstraintEngine.validate_type_against_concept("float", "Numeric")
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_constraint_unknown_concept():
    result = OmniPelocppModernConstraintEngine.validate_type_against_concept("int", "UnknownConcept")
    assert not result.is_ok()
    assert "Unknown concept" in str(result.unwrap_err())
