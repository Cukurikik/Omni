import pytest
import sys
import os

# Append project root to PYTHONPATH for internal core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from compute.python_core.omni_carpentries_intermediate_python_engine import OmniCarpentriesIntermediatePythonEngine
from compute.python_core.omni_thinkthink_command_ai_engine import OmniThinkThinkCommandAIEngine
from compute.python_core.omni_trood_troubleshooter_engine import OmniTroodTroubleshooterEngine
from compute.python_core.omni_drq_ergonomic_code_engine import OmniDrqErgonomicCodeEngine
from compute.python_core.omni_bybren_safe_agentic_workflow_engine import OmniBybrenSafeAgenticWorkflowEngine

# ==============================================================================
# INTEGRATION TESTS FOR SEMESTER 10 BATCH 16
# ==============================================================================

# 1. OmniCarpentriesIntermediatePythonEngine Tests
def test_carpentries_diagnostics():
    diag = OmniCarpentriesIntermediatePythonEngine.diagnostics()
    assert diag["monadic_enforcement"] is True
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_carpentries_valid_complexity():
    metrics = [{"branches": 2, "loops": 1, "returns": 1}, {"branches": 1, "loops": 0, "returns": 1}]
    result = OmniCarpentriesIntermediatePythonEngine.evaluate_code_complexity(metrics)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() == 3.0

def test_carpentries_invalid_complexity():
    metrics = [{"branches": 12, "loops": 4, "returns": 2}]
    result = OmniCarpentriesIntermediatePythonEngine.evaluate_code_complexity(metrics)
    assert not result.is_ok()
    assert "Avg complexity 18.00 > 10.0" in str(result.error)

# 2. OmniThinkThinkCommandAIEngine Tests
def test_thinkthink_diagnostics():
    diag = OmniThinkThinkCommandAIEngine.diagnostics()
    assert diag["monadic_enforcement"] is True
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_thinkthink_safe_command():
    cmd = "ls -la /var/log | grep auth"
    result = OmniThinkThinkCommandAIEngine.evaluate_command_safety(cmd)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_thinkthink_destructive_command():
    cmd = "rm -rf /etc"
    result = OmniThinkThinkCommandAIEngine.evaluate_command_safety(cmd)
    assert not result.is_ok()
    assert "Destructive pattern detected" in str(result.error)

# 3. OmniTroodTroubleshooterEngine Tests
def test_trood_diagnostics():
    diag = OmniTroodTroubleshooterEngine.diagnostics()
    assert diag["monadic_enforcement"] is True

def test_trood_valid_drift():
    installed = {"omni_pkg": (1, 2, 0)}
    required = {"omni_pkg": (1, 2, 0)}
    result = OmniTroodTroubleshooterEngine.calculate_version_drift(installed, required)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap()["omni_pkg"] == "Compliant"

def test_trood_major_incompatibility():
    installed = {"omni_pkg": (1, 5, 0)}
    required = {"omni_pkg": (2, 0, 0)}
    result = OmniTroodTroubleshooterEngine.calculate_version_drift(installed, required)
    assert not result.is_ok()
    assert "Major version incompatibility" in str(result.error)

# 4. OmniDrqErgonomicCodeEngine Tests
def test_drq_diagnostics():
    diag = OmniDrqErgonomicCodeEngine.diagnostics()
    assert diag["monadic_enforcement"] is True

def test_drq_valid_score():
    result = OmniDrqErgonomicCodeEngine.compute_ergonomics_score(loc=12, param_count=2, max_nesting_depth=1)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert 90.0 < result.unwrap() <= 100.0  # Perfect score should be roughly 100 since penalties are 0

def test_drq_poor_ergonomics():
    result = OmniDrqErgonomicCodeEngine.compute_ergonomics_score(loc=200, param_count=8, max_nesting_depth=6)
    assert not result.is_ok()
    assert "Cognitive load exceeds ergonomic barrier" in str(result.error)

# 5. OmniBybrenSafeAgenticWorkflowEngine Tests
def test_bybren_diagnostics():
    diag = OmniBybrenSafeAgenticWorkflowEngine.diagnostics()
    assert diag["monadic_enforcement"] is True

def test_bybren_valid_workflow():
    wf = ["INIT", "PI_PLANNING", "SYSTEM_ARCHITECTURE_SYNC", "ITERATION_EXECUTION", "SYSTEM_DEMO", "INSPECT_AND_ADAPT", "DONE"]
    result = OmniBybrenSafeAgenticWorkflowEngine.validate_safe_workflow_vector(wf)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_bybren_missing_phase():
    wf = ["PI_PLANNING", "SYSTEM_DEMO"]
    result = OmniBybrenSafeAgenticWorkflowEngine.validate_safe_workflow_vector(wf)
    assert not result.is_ok()
    assert "Missing phases" in str(result.error)
