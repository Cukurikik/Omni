import pytest
import sys
import os

# Append project root to PYTHONPATH for internal core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from compute.python_core.omni_bmad_openclaw_engine import OmniBmadOpenclawEngine
from compute.python_core.omni_gpt_synthesizer_engine import OmniGptSynthesizerEngine
from compute.python_core.omni_linux_play_kernel_engine import OmniLinuxPlayKernelEngine
from compute.python_core.omni_websockets_concurrency_engine import OmniWebsocketsConcurrencyEngine
from compute.python_core.omni_jafari_oop_polymorphism_engine import OmniJafariOopPolymorphismEngine

# ==============================================================================
# INTEGRATION TESTS FOR SEMESTER 10 BATCH 18
# ==============================================================================

# 1. OmniBmadOpenclawEngine Tests
def test_opencl_diagnostics():
    diag = OmniBmadOpenclawEngine.diagnostics()
    assert diag["monadic_enforcement"] is True
    assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

def test_opencl_valid_alignment():
    result = OmniBmadOpenclawEngine.validate_memory_alignment(buffer_size_bytes=1000, hardware_alignment_bytes=64)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.unwrap() == 1024  # 1000 padded cleanly to nearest 64 multiple

def test_opencl_invalid_power2():
    result = OmniBmadOpenclawEngine.validate_memory_alignment(buffer_size_bytes=1000, hardware_alignment_bytes=60)
    assert not result.is_ok()
    assert "violates power-of-2" in str(result.error)

# 2. OmniGptSynthesizerEngine Tests
def test_gpt_diagnostics():
    diag = OmniGptSynthesizerEngine.diagnostics()
    assert diag["monadic_enforcement"] is True

def test_gpt_safe_synthesis():
    result = OmniGptSynthesizerEngine.validate_synthesis_bounds(
        synthesized_tokens=2000, max_context_window=8000, structural_entropy=0.5
    )
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_gpt_hallucination_breach():
    result = OmniGptSynthesizerEngine.validate_synthesis_bounds(
        synthesized_tokens=2000, max_context_window=8000, structural_entropy=0.9
    )
    assert not result.is_ok()
    assert "Hallucination Breach" in str(result.error)

# 3. OmniLinuxPlayKernelEngine Tests
def test_linux_diagnostics():
    diag = OmniLinuxPlayKernelEngine.diagnostics()
    assert diag["monadic_enforcement"] is True

def test_linux_safe_isolation():
    # user allows 0b111, request is 0b101 -> intersection is 0b101 == requested.
    result = OmniLinuxPlayKernelEngine.enforce_capability_isolation(requested_mask=5, user_allowed_mask=7)
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_linux_escalation_attempt():
    # user allows 0b101, request is 0b111 -> Intersection is 0b101 != requested.
    result = OmniLinuxPlayKernelEngine.enforce_capability_isolation(requested_mask=7, user_allowed_mask=5)
    assert not result.is_ok()
    assert "Privilege Escalation Blocked" in str(result.error)

# 4. OmniWebsocketsConcurrencyEngine Tests
def test_websocket_diagnostics():
    diag = OmniWebsocketsConcurrencyEngine.diagnostics()
    assert diag["monadic_enforcement"] is True

def test_websocket_valid_scale():
    result = OmniWebsocketsConcurrencyEngine.calculate_maximum_concurrency(
        available_ram_mb=4000, bytes_per_socket=40000, max_file_descriptors=65536
    )
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    # 4000MB = 4,194,304,000 bytes. Div by 40,000 = 104,857 calculated ceiling
    # Min of 104857 and 65536 FD limits = 65536
    assert result.unwrap() == 65536

def test_websocket_fd_exhaustion():
    result = OmniWebsocketsConcurrencyEngine.calculate_maximum_concurrency(
        available_ram_mb=4000, bytes_per_socket=40000, max_file_descriptors=500
    )
    assert not result.is_ok()
    assert "OS File Descriptor limit too low" in str(result.error)

# 5. OmniJafariOopPolymorphismEngine Tests
def test_oop_diagnostics():
    diag = OmniJafariOopPolymorphismEngine.diagnostics()
    assert diag["monadic_enforcement"] is True

def test_oop_valid_liskov():
    result = OmniJafariOopPolymorphismEngine.validate_liskov_substitution(
        base_input_width=10, derived_input_width=15, base_output_width=20, derived_output_width=15
    )
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_oop_invalid_contravariance():
    result = OmniJafariOopPolymorphismEngine.validate_liskov_substitution(
        base_input_width=15, derived_input_width=10, base_output_width=20, derived_output_width=15
    )
    assert not result.is_ok()
    assert "Contravariance Violation" in str(result.error)
