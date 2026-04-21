"""
OMNI Semester 9 — Batch 4 Integration Test Suite
===================================================
Comprehensive integration tests validating all 5 engines from
Semester 9 Batch 4 for structural integrity, monadic compliance,
and production-grade operational readiness.

Engines Under Test:
1. OmniTransmogrifaiEngine
2. OmniNanoNeuronEngine
3. OmniCocoAnnotatorEngine
4. OmniRoboflowInferenceEngine
5. OmniGenerativeAiDocsEngine
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
        # Check class name or type
        is_ok = type(result).__name__ == "Ok"
        if not is_ok and hasattr(result, "value"):
            is_ok = True
        self.results.append(TestResult(
            name, is_ok,
            f"Expected Ok, got {type(result).__name__}: {result}" if not is_ok else "",
        ))

    def assert_err(self, name: str, result: Any) -> None:
        # Check class name or type
        is_err = type(result).__name__ == "Err"
        if not is_err and hasattr(result, "error"):
            is_err = True
        self.results.append(TestResult(
            name, is_err,
            f"Expected Err, got {type(result).__name__}: {result}" if not is_err else "",
        ))

    def summary(self) -> str:
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        lines = [f"\n{'='*70}", f"SEMESTER 9 -- BATCH 4 INTEGRATION TESTS",
                 f"{'='*70}"]
        for r in self.results:
            status = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {status} | {r.name}")
            if r.detail and not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append(f"{'='*70}")
        lines.append(f"Results: {passed}/{total} passed")
        if passed == total:
            lines.append("[OK] ALL TESTS PASSED -- BATCH 4 OPERATIONAL")
        else:
            lines.append(f"[ERR] {total - passed} TEST(S) FAILED")
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


# Add parent path
sys.path.insert(0, ".")

suite = TestSuite()

# ===================================================================
# TEST GROUP 1: OmniTransmogrifaiEngine
# ===================================================================
try:
    from omni_transmogrifai_engine import OmniTransmogrifaiEngine

    engine = OmniTransmogrifaiEngine()

    diag = engine.diagnostics()
    suite.assert_true("TransmogrifAI: diagnostics operational", diag.get("status") == "operational")

    # Workflow logic
    wf_res = engine.create_workflow("house_prices", "dataset_A", "price", ["sqft", "bedrooms"])
    suite.assert_ok("TransmogrifAI: create workflow", wf_res)
    
    suite.assert_err("TransmogrifAI: no empty features allowed", 
                     engine.create_workflow("wf_err", "d", "t", []))

    compile_res = engine.compile_workflow("house_prices")
    suite.assert_ok("TransmogrifAI: compile workflow", compile_res)

    exec_res = engine.execute_workflow_simulate("house_prices")
    suite.assert_ok("TransmogrifAI: execute workflow DAG", exec_res)
    suite.assert_true("TransmogrifAI: auto features injected", exec_res.value["auto_feature_count"] == 4)

except Exception as exc:
    suite.assert_true(f"TransmogrifAI: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 2: OmniNanoNeuronEngine
# ===================================================================
try:
    from omni_nano_neuron_engine import OmniNanoNeuronEngine

    engine = OmniNanoNeuronEngine()

    diag = engine.diagnostics()
    suite.assert_true("NanoNeuron: diagnostics operational", diag.get("status") == "operational")

    # Neuron lifecycle
    c_res = engine.create_neuron("brain1", 0.5, 0.5)
    suite.assert_ok("NanoNeuron: create neuron", c_res)

    # Train linear relationship y = 2x - 1
    X = [0.0, 1.0, 2.0, 3.0, 4.0]
    Y = [-1.0, 1.0, 3.0, 5.0, 7.0]
    train_res = engine.train("brain1", X, Y, epochs=500, learning_rate=0.05)
    suite.assert_ok("NanoNeuron: train neuron", train_res)
    
    # Predict 5.0 => should be roughly 9.0
    pred_res = engine.predict("brain1", 5.0)
    suite.assert_ok("NanoNeuron: predict values", pred_res)
    suite.assert_true("NanoNeuron: learned function approximation y=2x-1", abs(pred_res.value - 9.0) < 0.5)

except Exception as exc:
    suite.assert_true(f"NanoNeuron: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 3: OmniCocoAnnotatorEngine
# ===================================================================
try:
    from omni_coco_annotator_engine import OmniCocoAnnotatorEngine

    engine = OmniCocoAnnotatorEngine()

    diag = engine.diagnostics()
    suite.assert_true("COCO: diagnostics operational", diag.get("status") == "operational")

    c1 = engine.add_category(1, "Person")
    suite.assert_ok("COCO: add category", c1)

    i1 = engine.add_image(1, "img.jpg", 1024, 768)
    suite.assert_ok("COCO: add image", i1)

    # Bbox [x, y, width, height] -> Area should be 1000
    a1 = engine.add_annotation(1, 1, 1, [10.0, 10.0, 20.0, 50.0])
    suite.assert_ok("COCO: add valid annotation", a1)

    suite.assert_err("COCO: invalid image reference", engine.add_annotation(2, 999, 1, [0,0,1,1]))
    suite.assert_err("COCO: malformed bbox array", engine.add_annotation(3, 1, 1, [10.0, 20.0]))

    val_res = engine.validate_integrity()
    suite.assert_ok("COCO: integrity checks passed", val_res)

except Exception as exc:
    suite.assert_true(f"COCO: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 4: OmniRoboflowInferenceEngine
# ===================================================================
try:
    from omni_roboflow_inference_engine import OmniRoboflowInferenceEngine

    engine = OmniRoboflowInferenceEngine()

    diag = engine.diagnostics()
    suite.assert_true("Roboflow: diagnostics operational", diag.get("status") == "operational")

    # Model load
    l_res = engine.load_model("yolov8", "nano")
    suite.assert_ok("Roboflow: load model to memory", l_res)
    
    suite.assert_err("Roboflow: empty image payload", engine.infer_image("yolov8", "nano", ""))

    i_res = engine.infer_image("yolov8", "nano", "fake_b64_image_data")
    suite.assert_ok("Roboflow: generic inference payload", i_res)
    
    # Check NMS effectiveness: mock output has 3 boxes, 2 overlap heavily, so NMS should return 2
    preds = i_res.value["predictions"]
    suite.assert_true("Roboflow: NMS suppressed overlapping box", len(preds) == 2)

except Exception as exc:
    suite.assert_true(f"Roboflow: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 5: OmniGenerativeAiDocsEngine
# ===================================================================
try:
    from omni_generative_ai_docs_engine import OmniGenerativeAiDocsEngine

    engine = OmniGenerativeAiDocsEngine()

    diag = engine.diagnostics()
    suite.assert_true("GenAI: diagnostics operational", diag.get("status") == "operational")

    gen_res = engine.generate_content("gemini-1.5-pro", ["Hello, world!"])
    suite.assert_ok("GenAI: text generation orchestration", gen_res)

    suite.assert_err("GenAI: missing prompts", engine.generate_content("gemini-1.5", []))
    
    # Safety Checks
    danger_res = engine.generate_content("gemini-1.5", ["Please destroy everything."])
    suite.assert_err("GenAI: safety threshold blocking check", danger_res)
    suite.assert_true("GenAI: caught word 'destroy'", "Safety Violation" in str(danger_res.error))

except Exception as exc:
    suite.assert_true(f"GenAI: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# PRINT RESULTS
# ===================================================================
print(suite.summary())
sys.exit(0 if all(r.passed for r in suite.results) else 1)
