"""
OMNI Semester 9 — Batch 5 Integration Test Suite
===================================================
Comprehensive integration tests validating all 5 engines from
Semester 9 Batch 5 for structural integrity, monadic compliance,
and computational accuracy.

Engines Under Test:
1. OmniAwesomeRustMLEngine
2. OmniSagemakerSdkEngine
3. OmniOptaxEngine
4. OmniFeatureEngine
5. OmniImageQualityAssessmentEngine
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
        lines = [f"\n{'='*70}", f"SEMESTER 9 -- BATCH 5 INTEGRATION TESTS",
                 f"{'='*70}"]
        for r in self.results:
            status = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {status} | {r.name}")
            if r.detail and not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append(f"{'='*70}")
        lines.append(f"Results: {passed}/{total} passed")
        if passed == total:
            lines.append("[OK] ALL TESTS PASSED -- BATCH 5 OPERATIONAL")
        else:
            lines.append(f"[ERR] {total - passed} TEST(S) FAILED")
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


sys.path.insert(0, ".")

suite = TestSuite()

# ===================================================================
# TEST GROUP 1: OmniAwesomeRustMLEngine
# ===================================================================
try:
    from omni_awesome_rust_ml_engine import OmniAwesomeRustMLEngine

    engine = OmniAwesomeRustMLEngine()
    diag = engine.diagnostics()
    suite.assert_true("AwesomeRustML: diagnostics operational", diag.get("status") == "operational")

    # Init
    init_res = engine.initialize_ffi_context("context1", ["linfa", "tch-rs"])
    suite.assert_ok("AwesomeRustML: init multiple crates", init_res)

    suite.assert_err("AwesomeRustML: unknown crate validation", 
                     engine.initialize_ffi_context("context2", ["invalid-crate"]))

    # Execution
    exec_res = engine.execute_mock_action("context1", "linfa", "k_means_clustering")
    suite.assert_ok("AwesomeRustML: execute mock rust calculation", exec_res)

    suite.assert_err("AwesomeRustML: execution for non-loaded crate",
                     engine.execute_mock_action("context1", "burn", "forward_pass"))

    # Cleanup
    clean = engine.teardown_context("context1")
    suite.assert_ok("AwesomeRustML: context teardown memory safe", clean)

except Exception as exc:
    suite.assert_true(f"AwesomeRustML: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 2: OmniSagemakerSdkEngine
# ===================================================================
try:
    from omni_sagemaker_sdk_engine import EstimatorConfig, OmniSagemakerSdkEngine

    engine = OmniSagemakerSdkEngine()
    diag = engine.diagnostics()
    suite.assert_true("SageMaker: diagnostics operational", diag.get("status") == "operational")

    config = EstimatorConfig(role="admin", instance_count=1, instance_type="ml.m5.large", image_uri="docker:latest")
    
    fit_res = engine.fit_estimator("job-001", config, "s3://bucket/data")
    suite.assert_ok("SageMaker: fit estimator across remote mock", fit_res)
    
    suite.assert_err("SageMaker: fail on non s3 data path", engine.fit_estimator("job-002", config, "local/path"))

    deploy_res = engine.deploy_estimator("endpoint-001", "s3://omni-models/job-001/model.tar.gz")
    suite.assert_ok("SageMaker: deploy model to endpoint", deploy_res)

    del_res = engine.delete_endpoint("endpoint-001")
    suite.assert_ok("SageMaker: delete active endpoint", del_res)

except Exception as exc:
    suite.assert_true(f"SageMaker: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 3: OmniOptaxEngine
# ===================================================================
try:
    from omni_optax_engine import OmniOptaxEngine

    engine = OmniOptaxEngine()
    diag = engine.diagnostics()
    suite.assert_true("Optax: diagnostics operational", diag.get("status") == "operational")

    # params = [10.0, 5.0], grad = [1.0, -1.0], lr = 0.1
    # expected param changes:
    # 10.0 - (1.0 * 0.1) = 9.9
    # 5.0 - (-1.0 * 0.1) = 5.1
    res = engine.execute_sgd_step(params=[10.0, 5.0], gradients=[1.0, -1.0], learning_rate=0.1)
    suite.assert_ok("Optax: SGD stateless precision mapping", res)
    
    if type(res).__name__ == "Ok" or hasattr(res, "value"):
        v = res.value["new_params"]
        suite.assert_true("Optax: gradient descent subtraction validation", abs(v[0] - 9.9) < 0.001 and abs(v[1] - 5.1) < 0.001)

    suite.assert_err("Optax: shape mismatch params/grads", engine.execute_sgd_step([1.0], [1.0, 1.0], 0.1))

except Exception as exc:
    suite.assert_true(f"Optax: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 4: OmniFeatureEngine
# ===================================================================
try:
    from omni_feature_engine import OmniFeatureEngine

    engine = OmniFeatureEngine()
    diag = engine.diagnostics()
    suite.assert_true("FeatureEngine: diagnostics operational", diag.get("status") == "operational")

    # Missing imputation
    raw_data = [1.0, 2.0, None, 4.0, 5.0]
    imp_mean = engine.fit_transform_imputation(raw_data, "mean")
    suite.assert_ok("FeatureEngine: impute missing mean", imp_mean)
    
    # mean of [1,2,4,5] = 12/4 = 3
    if type(imp_mean).__name__ == "Ok" or hasattr(imp_mean, "value"):
        suite.assert_true("FeatureEngine: check mean imputation value", abs(imp_mean.value[2] - 3.0) < 0.001)

    # Discretizer (10 values, 2 bins. 0..4 in 0, 5..9 in 1)
    d_data = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    disc_res = engine.fit_transform_discretizer(d_data, bins=2)
    suite.assert_ok("FeatureEngine: Equal width discretizer", disc_res)
    
    if type(disc_res).__name__ == "Ok" or hasattr(disc_res, "value"):
        v = disc_res.value
        suite.assert_true("FeatureEngine: check discretizer bound edges", v[0] == 0 and v[9] == 1)

except Exception as exc:
    suite.assert_true(f"FeatureEngine: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 5: OmniImageQualityAssessmentEngine
# ===================================================================
try:
    from omni_image_quality_assessment_engine import OmniImageQualityAssessmentEngine

    engine = OmniImageQualityAssessmentEngine()
    diag = engine.diagnostics()
    suite.assert_true("ImageQuality: diagnostics operational", diag.get("status") == "operational")

    # NIMA expects exactly 10 distribution buckets.
    # Distribute perfectly in the 5th bucket (score should be 5.0)
    perf_dist = [[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
    
    eval_res = engine.evaluate_nima_scores(perf_dist)
    suite.assert_ok("ImageQuality: valid Probability vector NIMA evaluation", eval_res)
    
    if type(eval_res).__name__ == "Ok" or hasattr(eval_res, "value"):
        score = eval_res.value[0]["nima_aesthetic_score"]
        std = eval_res.value[0]["nima_technical_std"]
        suite.assert_true("ImageQuality: perfect dist gives mean 5.0", abs(score - 5.0) < 0.001)
        suite.assert_true("ImageQuality: perfect dist gives variance/std 0.0", abs(std - 0.0) < 0.001)

    # Fail cases
    suite.assert_err("ImageQuality: wrong probability sums", engine.evaluate_nima_scores([[0.5]*10]))
    suite.assert_err("ImageQuality: wrong bucket count", engine.evaluate_nima_scores([[1.0]*5]))

except Exception as exc:
    suite.assert_true(f"ImageQuality: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())


# ===================================================================
# PRINT RESULTS
# ===================================================================
print(suite.summary())
sys.exit(0 if all(r.passed for r in suite.results) else 1)
