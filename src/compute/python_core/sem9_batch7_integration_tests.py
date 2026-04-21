"""
OMNI Semester 9 — Batch 7 Integration Test Suite
===================================================
Comprehensive integration tests validating all 5 engines from
Semester 9 Batch 7 for structural integrity, monadic compliance,
and computational accuracy.

Engines Under Test:
1. OmniClassicPythonMLEngine
2. OmniNannyMlEngine
3. OmniNeuralPhotoEditorEngine
4. OmniAiRenamerEngine
5. OmniRecSysEngine
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
        lines = [f"\n{'='*70}", f"SEMESTER 9 -- BATCH 7 INTEGRATION TESTS",
                 f"{'='*70}"]
        for r in self.results:
            status = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {status} | {r.name}")
            if r.detail and not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append(f"{'='*70}")
        lines.append(f"Results: {passed}/{total} passed")
        if passed == total:
            lines.append("[OK] ALL TESTS PASSED -- BATCH 7 OPERATIONAL")
        else:
            lines.append(f"[ERR] {total - passed} TEST(S) FAILED")
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


sys.path.insert(0, ".")

suite = TestSuite()

# ===================================================================
# TEST GROUP 1: OmniClassicPythonMLEngine
# ===================================================================
try:
    from omni_classic_python_ml_engine import OmniClassicPythonMLEngine

    engine = OmniClassicPythonMLEngine()
    diag = engine.diagnostics()
    suite.assert_true("ClassicML: diagnostics operational", diag.get("status") == "operational")

    # KNN (Training features 1D mapped as 2D for engine logic)
    x_train = [[1.0], [2.0], [10.0], [11.0]]
    y_train = [0, 0, 1, 1]
    
    # Query point 2.5 is obviously Class 0
    res = engine.compute_knn_classification(x_train, y_train, [2.5], k=2)
    suite.assert_ok("ClassicML: KNN Math Logic prediction", res)
    
    if type(res).__name__ == "Ok" or hasattr(res, "value"):
        suite.assert_true("ClassicML: accurately predict Euclidean majority class 0", res.value["predicted_class"] == 0)

    # Errors
    suite.assert_err("ClassicML: catch empty query", engine.compute_knn_classification(x_train, y_train, [], k=2))
    suite.assert_err("ClassicML: Catch K out of bounds", engine.compute_knn_classification(x_train, y_train, [2.5], k=100))

except Exception as exc:
    suite.assert_true(f"ClassicML: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 2: OmniNannyMlEngine
# ===================================================================
try:
    from omni_nannyml_engine import OmniNannyMlEngine

    engine = OmniNannyMlEngine()
    diag = engine.diagnostics()
    suite.assert_true("NannyML: diagnostics operational", diag.get("status") == "operational")

    # Drift scenario: Exact same distributions should equal ~0 PSI
    ref = [1.0, 2.0, 3.0, 4.0, 5.0]
    prod = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    drift_res = engine.evaluate_model_drift(ref, prod, psi_threshold=0.2)
    suite.assert_ok("NannyML: Evaluate identical distribution", drift_res)
    
    if type(drift_res).__name__ == "Ok" or hasattr(drift_res, "value"):
        v = drift_res.value
        suite.assert_true("NannyML: Zero identical drift mapping", abs(v["psi_score"]) < 0.001)
        suite.assert_true("NannyML: No drift critical alert state", v["status"] == "stable")

    suite.assert_err("NannyML: Catch negative bins", engine.evaluate_model_drift(ref, prod, bins=0))

except Exception as exc:
    suite.assert_true(f"NannyML: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 3: OmniNeuralPhotoEditorEngine
# ===================================================================
try:
    from omni_neural_photo_editor_engine import OmniNeuralPhotoEditorEngine

    engine = OmniNeuralPhotoEditorEngine()
    diag = engine.diagnostics()
    suite.assert_true("NeuralPhoto: diagnostics operational", diag.get("status") == "operational")

    # SLERP (Spherical Linear Interpolation) mapping.
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0] # 90 degree angle (orthogonal)
    
    # Halfway (0.5) should equal [cos(45), sin(45)] = [0.707, 0.707]
    slerp_res = engine.compute_image_interpolation(v1, v2, transition_alpha=0.5)
    suite.assert_ok("NeuralPhoto: compute orthogonal SLERP math", slerp_res)
    
    if type(slerp_res).__name__ == "Ok" or hasattr(slerp_res, "value"):
        result_v = slerp_res.value["interpolated_generative_vector"]
        suite.assert_true("NeuralPhoto: Math equates to 45 degree vector space", 
                         abs(result_v[0] - 0.707) < 0.01 and abs(result_v[1] - 0.707) < 0.01)

    # Err cases
    suite.assert_err("NeuralPhoto: bounds safety limit", engine.compute_image_interpolation(v1, v2, 2.5))
    suite.assert_err("NeuralPhoto: dimension mismatch", engine.compute_image_interpolation([1.0], [1.0, 2.0]))

except Exception as exc:
    suite.assert_true(f"NeuralPhoto: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 4: OmniAiRenamerEngine
# ===================================================================
try:
    from omni_ai_renamer_engine import OmniAiRenamerEngine

    engine = OmniAiRenamerEngine()
    diag = engine.diagnostics()
    suite.assert_true("AiRenamer: diagnostics operational", diag.get("status") == "operational")

    class_res = engine.calculate_nomenclature(["Red Apple", "#Fruit!!"], target_casing="snake")
    suite.assert_ok("AiRenamer: Snake casing transformation", class_res)
    
    if type(class_res).__name__ == "Ok" or hasattr(class_res, "value"):
        filename = class_res.value["sanitized_file_name_prediction"]
        suite.assert_true("AiRenamer: Properly escaped filename generation", filename == "red_apple_fruit")

    # Tests camel Case
    camel_res = engine.calculate_nomenclature(["Cute dog", "puppy"], target_casing="camel")
    if type(camel_res).__name__ == "Ok" or hasattr(camel_res, "value"):
        filename = camel_res.value["sanitized_file_name_prediction"]
        suite.assert_true("AiRenamer: properly escaped camelCase", filename == "cuteDogPuppy")

    suite.assert_err("AiRenamer: unknown schemas blocked", 
                     engine.calculate_nomenclature(["Test"], target_casing="fake"))

except Exception as exc:
    suite.assert_true(f"AiRenamer: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 5: OmniRecSysEngine
# ===================================================================
try:
    from omni_rec_sys_engine import OmniRecSysEngine

    engine = OmniRecSysEngine()
    diag = engine.diagnostics()
    suite.assert_true("RecSys: diagnostics operational", diag.get("status") == "operational")

    # User item ratings matrix (3 users, 3 items)
    matrix = [
        [5.0, 3.0, 0.0], # User 1
        [4.0, 0.0, 0.0], # User 2
        [1.0, 1.0, 5.0], # User 3
    ]
    
    rec_res = engine.compute_collaborative_filtering(matrix)
    suite.assert_ok("RecSys: Cosine execution matrix generated", rec_res)
    
    suite.assert_err("RecSys: Too sparse dimensions", engine.compute_collaborative_filtering([[1.0]]))

except Exception as exc:
    suite.assert_true(f"RecSys: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())


# ===================================================================
# PRINT RESULTS
# ===================================================================
print(suite.summary())
sys.exit(0 if all(r.passed for r in suite.results) else 1)
