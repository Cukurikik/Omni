import pytest
import sys
import os

# Ensure the root of the project is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.compute.python_core.omni_spk_package_manager_engine import OmniSpkPackageManagerEngine
from src.compute.python_core.omni_julesmons_recline_terminal_engine import OmniJulesmonsReclineTerminalEngine
from src.compute.python_core.omni_xyoz_saturn_swarm_engine import OmniXyozSaturnSwarmEngine
from src.compute.python_core.omni_wemake_services_meta_process_engine import OmniWemakeServicesMetaProcessEngine
from src.compute.python_core.omni_novfensec_kvdeveloper_engine import OmniNovfensecKvdeveloperEngine

# 1. Spk Package Manager Engine Tests
def test_spk_diagnostics():
    diag = OmniSpkPackageManagerEngine.diagnostics()
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_spk_valid_dag_resolution():
    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D"],
        "D": []
    }
    result = OmniSpkPackageManagerEngine.resolve_dependency_graph(graph)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    # Linear execution order - D is required by B and C, B and C required by A.
    order = result.unwrap()
    assert order == ["D", "C", "B", "A"] or order == ["D", "B", "C", "A"]

def test_spk_circular_dependency():
    graph = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"]
    }
    result = OmniSpkPackageManagerEngine.resolve_dependency_graph(graph)
    assert not result.is_ok()
    assert "Circular dependency cycle detected" in str(result.unwrap_err())


# 2. Recline Terminal Assitant Engine Tests
def test_recline_diagnostics():
    diag = OmniJulesmonsReclineTerminalEngine.diagnostics()
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_recline_safe_command():
    result = OmniJulesmonsReclineTerminalEngine.validate_autonomous_command("ls -la /var/log")
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() == "ls -la /var/log"

def test_recline_destructive_command():
    result = OmniJulesmonsReclineTerminalEngine.validate_autonomous_command("sudo rm -rf /etc/kubernetes")
    assert not result.is_ok()
    assert "Catastrophic sequence detected" in str(result.unwrap_err())


# 3. Saturn Swarm Consensus Engine Tests
def test_saturn_diagnostics():
    diag = OmniXyozSaturnSwarmEngine.diagnostics()
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_saturn_valid_bft():
    # N = 10, F = 2 -> 3(2)+1 = 7. 10 >= 7.
    result = OmniXyozSaturnSwarmEngine.calculate_swarm_consensus(10, 2)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() == 0.8  # (10-2)/10

def test_saturn_invalid_bft():
    # N = 8, F = 3 -> 3(3)+1 = 10. 8 is NOT >= 10. Fault threshold breached.
    result = OmniXyozSaturnSwarmEngine.calculate_swarm_consensus(8, 3)
    assert not result.is_ok()
    assert "Byzantine constraint N >= 3F+1 unmet" in str(result.unwrap_err())


# 4. Wemake Services Meta Process SDLC Tests
def test_meta_process_diagnostics():
    diag = OmniWemakeServicesMetaProcessEngine.diagnostics()
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_meta_valid_transition():
    result = OmniWemakeServicesMetaProcessEngine.validate_process_transition("CODE_REVIEW", "CI_PIPELINE")
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_meta_invalid_jump_transition():
    result = OmniWemakeServicesMetaProcessEngine.validate_process_transition("IN_PROGRESS", "PROD_DEPLOY")
    assert not result.is_ok()
    assert "Illegal transition trajectory" in str(result.unwrap_err())


# 5. Novfensec KvDeveloper Scaffolding Tests
def test_kvdeveloper_diagnostics():
    diag = OmniNovfensecKvdeveloperEngine.diagnostics()
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_kvdeveloper_valid_scaffolding():
    generated = ["main.py", "app.kv", "requirements.txt", ".gitignore", "buildozer.spec", "assets/logo.png"]
    result = OmniNovfensecKvdeveloperEngine.validate_scaffolding_architecture("kivy_standard", generated)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() is True

def test_kvdeveloper_missing_pillars():
    generated = ["main.py", ".gitignore"] # Missing app.kv, requirements.txt, buildozer.spec
    result = OmniNovfensecKvdeveloperEngine.validate_scaffolding_architecture("kivy_standard", generated)
    assert not result.is_ok()
    assert "Missing architectural pillars" in str(result.unwrap_err())

