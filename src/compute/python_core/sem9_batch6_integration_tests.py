"""
OMNI Semester 9 — Batch 6 Integration Test Suite
===================================================
Comprehensive integration tests validating all 5 engines from
Semester 9 Batch 6 for structural integrity, monadic compliance,
and computational accuracy.

Engines Under Test:
1. OmniRasterVisionEngine
2. OmniRubyMlInteropEngine
3. OmniPyTextRankEngine
4. OmniGeneticAlgorithmEngine
5. OmniEasyNlpEngine
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
    name: str
    passed: bool
    detail: str = ""


class TestSuite:
    def __init__(self) -> None:
        self.results: List[TestResult] = []

    def assert_true(self, name: str, condition: bool, detail: str = "") -> None:
        self.results.append(TestResult(name, condition, detail))

    def assert_ok(self, name: str, result: Any) -> None:
        is_ok = type(result).__name__ == "Ok" or hasattr(result, "value")
        self.results.append(TestResult(
            name, is_ok,
            f"Expected Ok, got {type(result).__name__}: {result}" if not is_ok else "",
        ))

    def assert_err(self, name: str, result: Any) -> None:
        is_err = type(result).__name__ == "Err" or hasattr(result, "error")
        self.results.append(TestResult(
            name, is_err,
            f"Expected Err, got {type(result).__name__}: {result}" if not is_err else "",
        ))

    def summary(self) -> str:
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        lines = [f"\n{'='*70}", f"SEMESTER 9 -- BATCH 6 INTEGRATION TESTS",
                 f"{'='*70}"]
        for r in self.results:
            status = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {status} | {r.name}")
            if r.detail and not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append(f"{'='*70}")
        lines.append(f"Results: {passed}/{total} passed")
        if passed == total:
            lines.append("[OK] ALL TESTS PASSED -- BATCH 6 OPERATIONAL")
        else:
            lines.append(f"[ERR] {total - passed} TEST(S) FAILED")
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


sys.path.insert(0, ".")

suite = TestSuite()

# ===================================================================
# TEST GROUP 1: OmniRasterVisionEngine
# ===================================================================
try:
    from omni_raster_vision_engine import OmniRasterVisionEngine

    engine = OmniRasterVisionEngine()
    diag = engine.diagnostics()
    suite.assert_true("RasterVision: diagnostics operational", diag.get("status") == "operational")

    # Generate Chips math (Height 10, width 10, chip 5, stride 5 = 4 perfect chips)
    chip_res = engine.generate_sliding_windows(10, 10, 5, 5)
    suite.assert_ok("RasterVision: Sliding window matrix math", chip_res)
    
    if type(chip_res).__name__ == "Ok" or hasattr(chip_res, "value"):
        suite.assert_true("RasterVision: Verify exactly 4 windows derived", chip_res.value["total_windows_generated"] == 4)

    suite.assert_err("RasterVision: Fail gracefully on negative extents", engine.generate_sliding_windows(-1, 10, 5, 5))
    suite.assert_err("RasterVision: Prevent infinite loop zero stride", engine.generate_sliding_windows(10, 10, 5, 0))

except Exception as exc:
    suite.assert_true(f"RasterVision: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 2: OmniRubyMlInteropEngine
# ===================================================================
try:
    from omni_ruby_ml_interop_engine import OmniRubyMlInteropEngine

    engine = OmniRubyMlInteropEngine()
    diag = engine.diagnostics()
    suite.assert_true("RubyInterop: diagnostics operational", diag.get("status") == "operational")

    cat = engine.fetch_ruby_ecosystem()
    suite.assert_true("RubyInterop: Verify known gems available", "rumale" in cat)

    launch_res = engine.launch_ruby_vm_context("ctx-ruby-1", ["rumale"])
    suite.assert_ok("RubyInterop: Spin up VM context via FFI algebraic_bound", launch_res)
    
    suite.assert_err("RubyInterop: Fail if unknown gem requested", engine.launch_ruby_vm_context("ctx-ruby-2", ["fake-gem"]))

    route_res = engine.route_computational_payload("ctx-ruby-1", "rumale", "fit_predict", "(100x100)")
    suite.assert_ok("RubyInterop: Transmit computation across boundary", route_res)

    suite.assert_err("RubyInterop: Prevent routing to destroyed context", engine.route_computational_payload("x", "x", "x", "x"))

    sd_res = engine.shutdown_ruby_vm("ctx-ruby-1")
    suite.assert_ok("RubyInterop: Context correctly destroyed", sd_res)

except Exception as exc:
    suite.assert_true(f"RubyInterop: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 3: OmniPyTextRankEngine
# ===================================================================
try:
    from omni_py_text_rank_engine import OmniPyTextRankEngine

    engine = OmniPyTextRankEngine()
    diag = engine.diagnostics()
    suite.assert_true("PyTextRank: diagnostics operational", diag.get("status") == "operational")

    # [A, B, C, A, B] graph loop logic
    tokens = ["A", "B", "C", "A", "B"]
    tr_res = engine.compute_text_ranking(tokens, window_size=2)
    suite.assert_ok("PyTextRank: Compute Graph Math Ranking", tr_res)
    
    if type(tr_res).__name__ == "Ok" or hasattr(tr_res, "value"):
        v = tr_res.value
        suite.assert_true("PyTextRank: Identifies 3 unique vocabulary items", v["vocabulary_size"] == 3)

    suite.assert_err("PyTextRank: Reject invalid window size", engine.compute_text_ranking(["A", "B"], window_size=1))
    suite.assert_err("PyTextRank: Reject empty tokens", engine.compute_text_ranking([]))

except Exception as exc:
    suite.assert_true(f"PyTextRank: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 4: OmniGeneticAlgorithmEngine
# ===================================================================
try:
    from omni_genetic_algorithm_engine import OmniGeneticAlgorithmEngine

    engine = OmniGeneticAlgorithmEngine()
    diag = engine.diagnostics()
    suite.assert_true("GeneticAlgorithm: diagnostics operational", diag.get("status") == "operational")

    # 4 individuals, shape (4, 4)
    population = [
        [1.0, 1.0, 1.0, 1.0],
        [2.0, 2.0, 2.0, 2.0],
        [3.0, 3.0, 3.0, 3.0],
        [4.0, 4.0, 4.0, 4.0]
    ]
    # Fitness values (Best are index 2 and 3)
    fitness = [10.0, 20.0, 500.0, 1000.0]

    gen_res = engine.compute_generation(population, fitness, num_parents=2)
    suite.assert_ok("GeneticAlgorithm: Core Execution Vector calculation", gen_res)
    
    if type(gen_res).__name__ == "Ok" or hasattr(gen_res, "value"):
        v = gen_res.value
        # Parents should correctly identify index 3 and 2 (values 4.0 and 3.0)
        suite.assert_true("GeneticAlgorithm: Highest fitness rank truncation check", v["parents"][0][0] == 4.0)

    suite.assert_err("GeneticAlgorithm: Shape mismatch safeguard", engine.compute_generation(population, [1.0], 2))

except Exception as exc:
    suite.assert_true(f"GeneticAlgorithm: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 5: OmniEasyNlpEngine
# ===================================================================
try:
    from omni_easy_nlp_engine import OmniEasyNlpEngine

    engine = OmniEasyNlpEngine()
    diag = engine.diagnostics()
    suite.assert_true("EasyNLP: diagnostics operational", diag.get("status") == "operational")

    res = engine.invoke_app_zoo_pipeline("text_classify", ["Valid text structure evaluating logic."], max_sequence=16)
    suite.assert_ok("EasyNLP: Text classify logic flow simulated", res)

    suite.assert_err("EasyNLP: Block unsupported pipeline tasks", engine.invoke_app_zoo_pipeline("fake_task", ["hi"]))

except Exception as exc:
    suite.assert_true(f"EasyNLP: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())


# ===================================================================
# PRINT RESULTS
# ===================================================================
print(suite.summary())
sys.exit(0 if all(r.passed for r in suite.results) else 1)
