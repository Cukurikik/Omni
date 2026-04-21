"""
OMNI Semester 9 — Batch 3 Integration Test Suite
===================================================
Comprehensive integration tests validating all 6 engines from
Semester 9 Batch 3 for structural integrity, monadic compliance,
and production-grade operational readiness.

Engines Under Test:
1. OmniMlRetreatEngine
2. OmniTangentEngine
3. OmniScattertextEngine
4. OmniAutolabelEngine
5. OmniKarateclubEngine
6. OmniBulbeaEngine
"""

from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from typing import Any, List

import numpy as np

# ---------------------------------------------------------------------------
# Test Framework
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    """Result of a single test case."""
    name: str
    passed: bool
    detail: str = ""


class TestSuite:
    """Lightweight test runner."""

    def __init__(self) -> None:
        self.results: List[TestResult] = []

    def assert_true(self, name: str, condition: bool, detail: str = "") -> None:
        self.results.append(TestResult(name, condition, detail))

    def assert_ok(self, name: str, result: Any) -> None:
        from omni_ml_retreat_engine import Ok
        is_ok = type(result).__name__ == "Ok" or isinstance(result, Ok)
        self.results.append(TestResult(
            name, is_ok,
            f"Expected Ok, got {type(result).__name__}: {result}" if not is_ok else "",
        ))

    def assert_err(self, name: str, result: Any) -> None:
        from omni_ml_retreat_engine import Err
        is_err = type(result).__name__ == "Err" or isinstance(result, Err)
        self.results.append(TestResult(
            name, is_err,
            f"Expected Err, got {type(result).__name__}" if not is_err else "",
        ))

    def summary(self) -> str:
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        lines = [f"\n{'='*70}", f"SEMESTER 9 -- BATCH 3 INTEGRATION TESTS",
                 f"{'='*70}"]
        for r in self.results:
            status = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {status} | {r.name}")
            if r.detail and not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append(f"{'='*70}")
        lines.append(f"Results: {passed}/{total} passed")
        if passed == total:
            lines.append("[OK] ALL TESTS PASSED -- BATCH 3 OPERATIONAL")
        else:
            lines.append(f"[ERR] {total - passed} TEST(S) FAILED")
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


# Add parent path
sys.path.insert(0, ".")

suite = TestSuite()

# ===================================================================
# TEST GROUP 1: OmniMlRetreatEngine
# ===================================================================
try:
    from omni_ml_retreat_engine import OmniMlRetreatEngine

    engine = OmniMlRetreatEngine()

    # T1.1 - Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("MLRetreat: diagnostics operational", isinstance(diag, dict) and diag.get("status") == "operational")

    # T1.2 - Attention mechanism
    Q = np.random.randn(1, 4, 16)
    K = np.random.randn(1, 4, 16)
    V = np.random.randn(1, 4, 32)
    att_res = engine.attention(Q, K, V)
    suite.assert_ok("MLRetreat: scaled dot product attention", att_res)

    # T1.3 - EBM
    engine.register_ebm("test_ebm", lambda x: float(np.sum(x**2)))
    ebm_eval = engine.evaluate_ebm("test_ebm", np.array([1, 2]))
    suite.assert_ok("MLRetreat: evaluate energy", ebm_eval)

    # T1.4 - QML Circuit
    qml_res = engine.create_qml_circuit(2)
    suite.assert_ok("MLRetreat: QML circuit creation", qml_res)
    circuit = qml_res.value
    circuit.apply_hadamard_all()
    probs = circuit.measure_probabilities()
    suite.assert_ok("MLRetreat: QML probabilities measurement", probs)

except Exception as exc:
    suite.assert_true(f"MLRetreat: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 2: OmniTangentEngine
# ===================================================================
try:
    from omni_tangent_engine import OmniTangentEngine

    engine = OmniTangentEngine()

    # T2.1 - Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Tangent: diagnostics operational", diag.get("status") == "operational")

    # T2.2 - Register function and get Forward derivative
    def square(x): return x**2
    engine.register_function("sq", square)
    grad_res = engine.grad("sq", np.array([3.0]))
    suite.assert_ok("Tangent: gradient computation", grad_res)
    # Derivative of x^2 at 3 is 6
    suite.assert_true("Tangent: correct gradient value", np.allclose(grad_res.value, 6.0, atol=1e-3))

    # T2.3 - Reverse derivative VJP
    vjp_res = engine.vjp("sq", np.array([3.0]), np.array([2.0]))
    suite.assert_ok("Tangent: VJP computation", vjp_res)

    # T2.4 - Invalid gradients wrapper
    suite.assert_err("Tangent: non array string input", engine.grad("sq", "hello"))

except Exception as exc:
    suite.assert_true(f"Tangent: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 3: OmniScattertextEngine
# ===================================================================
try:
    from omni_scattertext_engine import OmniScattertextEngine

    engine = OmniScattertextEngine()

    # T3.1 - Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Scattertext: diagnostics operational", diag.get("status") == "operational")

    # T3.2 - Ingest docs
    engine.ingest_document("democrat", ["tax", "healthcare", "equality"])
    engine.ingest_document("republican", ["tax", "military", "liberty"])
    
    # T3.3 - Substantial error blocks
    eval_res = engine.evaluate_terms("democrat")
    suite.assert_ok("Scattertext: evaluate term associations", eval_res)
    
    suite.assert_err("Scattertext: evaluate nonexistent category", engine.evaluate_terms("green_party"))

except Exception as exc:
    suite.assert_true(f"Scattertext: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 4: OmniAutolabelEngine
# ===================================================================
try:
    from omni_autolabel_engine import OmniAutolabelEngine

    engine = OmniAutolabelEngine()

    # T4.1 - Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Autolabel: diagnostics operational", diag.get("status") == "operational")

    # T4.2 - Register Task
    reg_task = engine.register_task("sentiment", "classification", "openai", "gpt-3.5",
                                    "Classify sentiment of {input}", ["positive", "negative"])
    suite.assert_ok("Autolabel: register task", reg_task)

    # T4.3 - Run Labeling
    lab_res = engine.run_labeling("sentiment", ["This is great!", "Terrible service."])
    suite.assert_ok("Autolabel: run labeling pipeline", lab_res)
    suite.assert_true("Autolabel: returned correct batch size", len(lab_res.value) == 2)

    # T4.4 - Error Handling
    suite.assert_err("Autolabel: empty inputs", engine.run_labeling("sentiment", []))

except Exception as exc:
    suite.assert_true(f"Autolabel: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 5: OmniKarateclubEngine
# ===================================================================
try:
    from omni_karateclub_engine import OmniKarateclubEngine

    engine = OmniKarateclubEngine()

    # T5.1 - Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Karateclub: diagnostics operational", diag.get("status") == "operational")

    # T5.2 - Graph operations
    build_res = engine.build_graph([[1, 2], [2, 3], [4, 5]])
    suite.assert_ok("Karateclub: build graph", build_res)

    # T5.3 - Random Walks
    walk_res = engine.deep_walks(walks_per_node=2, walk_length=5)
    suite.assert_ok("Karateclub: deep walks", walk_res)

    # T5.4 - Communities
    comm_res = engine.detect_communities()
    suite.assert_ok("Karateclub: community detection", comm_res)
    suite.assert_true("Karateclub: counted two disjoint chunks", comm_res.value["communities_count"] == 2)

except Exception as exc:
    suite.assert_true(f"Karateclub: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 6: OmniBulbeaEngine
# ===================================================================
try:
    from omni_bulbea_engine import OmniBulbeaEngine

    engine = OmniBulbeaEngine()

    # T6.1 - Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Bulbea: diagnostics operational", diag.get("status") == "operational")

    # T6.2 - Load equity
    load_res = engine.load_equity("AAPL", [150.0, 151.0, 152.5, 149.0, 153.2, 155.0, 154.5, 156.0])
    suite.assert_ok("Bulbea: load stock sequence", load_res)

    # T6.3 - Sequence modeling
    lstm_res = engine.prepare_lstm_data("AAPL", window_size=3, test_split=0.2)
    suite.assert_ok("Bulbea: prepare LSTM sequencing", lstm_res)

    # T6.4 - Error bounds
    suite.assert_err("Bulbea: invalid window size bounds error", engine.prepare_lstm_data("AAPL", window_size=99))

except Exception as exc:
    suite.assert_true(f"Bulbea: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# PRINT RESULTS
# ===================================================================
print(suite.summary())
sys.exit(0 if all(r.passed for r in suite.results) else 1)
