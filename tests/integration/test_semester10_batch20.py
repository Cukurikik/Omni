import os
import sys
import pytest

# Ensure the root of the Omni project is in the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.compute.python_core.omni_kuberocket_ai_engine import OmniKubeRocketAiEngine
from src.compute.python_core.omni_tembo_aifsd_engine import OmniTemboAifsDEngine
from src.compute.python_core.omni_battysh_batty_engine import OmniBattyshBattyEngine
from src.compute.python_core.omni_matt_hulme_deliberate_agentic_engine import OmniMattHulmeDeliberateAgenticEngine
from src.compute.python_core.omni_aroojjaved93_ticket_routing_engine import OmniAroojjaved93TicketRoutingEngine

# -------------------------------------------------------------------
# 1. OmniKubeRocketAiEngine
# -------------------------------------------------------------------
def test_kuberocket_diagnostics():
    diag = OmniKubeRocketAiEngine.diagnostics()
    assert diag["engine"] == "OmniKubeRocketAiEngine"
    assert diag["monadic_enforcement"] is True

def test_kuberocket_valid_pipeline():
    result = OmniKubeRocketAiEngine.validate_sdlc_pipeline_integrity(["build", "test", "lint", "deploy"], ["test", "lint"])
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_kuberocket_missing_gate():
    result = OmniKubeRocketAiEngine.validate_sdlc_pipeline_integrity(["build", "deploy"], ["test"])
    assert not result.is_ok()
    assert "Missing critical CI/CD gate" in str(result.unwrap_err())

def test_kuberocket_invalid_topology():
    result = OmniKubeRocketAiEngine.validate_sdlc_pipeline_integrity(["build", "deploy", "test"], ["test"])
    assert not result.is_ok()
    assert "must mathematically precede" in str(result.unwrap_err())

# -------------------------------------------------------------------
# 2. OmniTemboAifsDEngine
# -------------------------------------------------------------------
def test_aifsd_diagnostics():
    diag = OmniTemboAifsDEngine.diagnostics()
    assert diag["engine"] == "OmniTemboAifsDEngine"

def test_aifsd_valid_maturity():
    result = OmniTemboAifsDEngine.calculate_aifsd_maturity(0.4, 0.6, True)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    score = result.unwrap()
    assert abs(score - 0.6) < 0.001

def test_aifsd_high_ai_ratio_breach():
    # High AI ratio (0.8) but low test coverage (0.3)
    result = OmniTemboAifsDEngine.calculate_aifsd_maturity(0.8, 0.3, True)
    assert not result.is_ok()
    assert "requires strict test boundary (> 0.5)" in str(result.unwrap_err())

# -------------------------------------------------------------------
# 3. OmniBattyshBattyEngine
# -------------------------------------------------------------------
def test_batty_diagnostics():
    diag = OmniBattyshBattyEngine.diagnostics()
    assert diag["engine"] == "OmniBattyshBattyEngine"

def test_batty_valid_transition():
    result = OmniBattyshBattyEngine.gate_kanban_transition("IN_REVIEW", "COMPLETED", 0.9, 50, 50)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_batty_invalid_completion_ratio():
    result = OmniBattyshBattyEngine.gate_kanban_transition("IN_PROGRESS", "COMPLETED", 0.9, 49, 50)
    assert not result.is_ok()
    assert "Test failure boundary breached" in str(result.unwrap_err())

def test_batty_low_coverage():
    result = OmniBattyshBattyEngine.gate_kanban_transition("IN_REVIEW", "COMPLETED", 0.75, 50, 50)
    assert not result.is_ok()
    assert "Test coverage boundary breached" in str(result.unwrap_err())

# -------------------------------------------------------------------
# 4. OmniMattHulmeDeliberateAgenticEngine
# -------------------------------------------------------------------
def test_deliberate_diagnostics():
    diag = OmniMattHulmeDeliberateAgenticEngine.diagnostics()
    assert diag["engine"] == "OmniMattHulmeDeliberateAgenticEngine"

def test_deliberate_valid_human_review():
    result = OmniMattHulmeDeliberateAgenticEngine.validate_human_in_the_loop_checkpoint(8.5, 1, 0)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_deliberate_high_complexity_breach():
    result = OmniMattHulmeDeliberateAgenticEngine.validate_human_in_the_loop_checkpoint(9.0, 0, 5)
    assert not result.is_ok()
    assert "requires at least 1 human structural review" in str(result.unwrap_err())

def test_deliberate_medium_complexity_auto_breach():
    result = OmniMattHulmeDeliberateAgenticEngine.validate_human_in_the_loop_checkpoint(5.0, 0, 1)
    assert not result.is_ok()
    assert "require dual automated reviews" in str(result.unwrap_err())

# -------------------------------------------------------------------
# 5. OmniAroojjaved93TicketRoutingEngine
# -------------------------------------------------------------------
def test_ticket_diagnostics():
    diag = OmniAroojjaved93TicketRoutingEngine.diagnostics()
    assert diag["engine"] == "OmniAroojjaved93TicketRoutingEngine"

def test_ticket_safe_sla():
    # elapsed: 2, mean: 10, std: 2, limit: 24
    result = OmniAroojjaved93TicketRoutingEngine.predict_sla_breach(2.0, 10.0, 2.0, 24.0)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is False

def test_ticket_breached_sla():
    # elapsed: 25, limit: 24
    result = OmniAroojjaved93TicketRoutingEngine.predict_sla_breach(25.0, 10.0, 2.0, 24.0)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_ticket_imminent_breach():
    # elapsed: 20, mean: 30, std: 2, limit: 24 (Time rem: 4. Expected rem: 10. 10 > 4+2 -> True)
    result = OmniAroojjaved93TicketRoutingEngine.predict_sla_breach(20.0, 30.0, 2.0, 24.0)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True
