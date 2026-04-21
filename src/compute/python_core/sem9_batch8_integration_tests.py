"""
OMNI Semester 9 — Batch 8 Integration Test Suite
===================================================
Comprehensive integration tests validating all 5 engines from
Semester 9 Batch 8 for structural data geometry, spatial bounds mapping,
and monadic computational compliance.

Engines Under Test:
1. OmniUniversalDataToolEngine
2. OmniNsfwFilterEngine
3. OmniRobosatEngine
4. OmniOrbitBayesianEngine
5. OmniModel2VecEngine
"""

from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from typing import Any, List

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
        lines = [f"\n{'='*70}", f"SEMESTER 9 -- BATCH 8 INTEGRATION TESTS",
                 f"{'='*70}"]
        for r in self.results:
            status = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {status} | {r.name}")
            if r.detail and not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append(f"{'='*70}")
        lines.append(f"Results: {passed}/{total} passed")
        if passed == total:
            lines.append("[OK] ALL TESTS PASSED -- BATCH 8 OPERATIONAL")
        else:
            lines.append(f"[ERR] {total - passed} TEST(S) FAILED")
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


sys.path.insert(0, ".")

suite = TestSuite()

# ===================================================================
# TEST GROUP 1: OmniUniversalDataToolEngine
# ===================================================================
try:
    from omni_universal_data_tool_engine import OmniUniversalDataToolEngine

    engine = OmniUniversalDataToolEngine()
    diag = engine.diagnostics()
    suite.assert_true("UDT: diagnostics operational", diag.get("status") == "operational")

    # Safe layout sample
    safe_samples = [
        {
            "imageUrl": "img1.jpg",
            "region": [
                {"label": "dog", "box2d": {"x": 10.0, "y": 10.0, "width": 50.0, "height": 50.0}}
            ]
        },
        {
            "imageUrl": "img2.jpg",
            "region": [
               # Invalid Bounding box (missing width)
               {"label": "cat", "box2d": {"x": 0.0, "y": 0.0, "height": 10.0}}
            ]
        }
    ]
    
    res = engine.validate_and_transform_dataset(safe_samples)
    suite.assert_ok("UDT: Matrix evaluation format successfully", res)
    
    if type(res).__name__ == "Ok" or hasattr(res, "value"):
        val = res.value
        suite.assert_true("UDT: Accurately dropped 1 invalid schema region", val["invalid_samples_dropped"] == 1)
        schema_labels = val["udt_compiled_schema"]["interface"]["labels"]
        suite.assert_true("UDT: Schema constructed correctly capturing valid known labels", "dog" in schema_labels and "cat" not in schema_labels)

    suite.assert_err("UDT: catch empty struct", engine.validate_and_transform_dataset([]))

except Exception as exc:
    suite.assert_true(f"UDT: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 2: OmniNsfwFilterEngine
# ===================================================================
try:
    from omni_nsfw_filter_engine import OmniNsfwFilterEngine

    engine = OmniNsfwFilterEngine()
    diag = engine.diagnostics()
    suite.assert_true("NSFW: diagnostics operational", diag.get("status") == "operational")

    probs = {
        "drawings": 0.05,
        "porn": 0.55,
        "neutral": 0.1,
        "hentai": 0.02
    }
    
    gate_res = engine.evaluate_probability_distribution(probs, explicit_block_level=0.51, soft_review_level=0.7)
    suite.assert_ok("NSFW: Vector summation mapping cleanly", gate_res)
    
    if type(gate_res).__name__ == "Ok" or hasattr(gate_res, "value"):
        v = gate_res.value["moderation_resolution"]
        suite.assert_true("NSFW: Explicit gate appropriately breached triggering rejection", v["verdict"] == "REJECTED_EXPLICIT")

    suite.assert_err("NSFW: Catch invalid out of bounds", engine.evaluate_probability_distribution(probs, explicit_block_level=9.0))
    suite.assert_err("NSFW: Non numeric strings rejected", engine.evaluate_probability_distribution({"porn": "text"}))

except Exception as exc:
    suite.assert_true(f"NSFW: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 3: OmniRobosatEngine
# ===================================================================
try:
    from omni_robosat_engine import OmniRobosatEngine

    engine = OmniRobosatEngine()
    diag = engine.diagnostics()
    suite.assert_true("Robosat: diagnostics operational", diag.get("status") == "operational")

    # Zoom 14 Lat/Lon box
    robo_res = engine.compute_tile_extents(
        bbox_min_lat=40.0, bbox_min_lon=-74.0,  # NYC Area roughly
        bbox_max_lat=40.1, bbox_max_lon=-73.9,
        zoom_level=14
    )
    suite.assert_ok("Robosat: Compute Slippy XYZ tiles math map", robo_res)
    
    if type(robo_res).__name__ == "Ok" or hasattr(robo_res, "value"):
        xyz_coords = robo_res.value["grid_coordinates_xyz"]
        suite.assert_true("Robosat: Return exact bounded matrices arrays", len(xyz_coords) > 0)

    # Err constraints
    suite.assert_err("Robosat: Catch flipped Min/Max boundaries", engine.compute_tile_extents(40.0, -74.0, 39.0, -74.0))
    suite.assert_err("Robosat: Block destructive Zoom depth Memory exhaustions", engine.compute_tile_extents(0, 0, 1, 1, zoom_level=999))

except Exception as exc:
    suite.assert_true(f"Robosat: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 4: OmniOrbitBayesianEngine
# ===================================================================
try:
    from omni_orbit_bayesian_engine import OmniOrbitBayesianEngine

    engine = OmniOrbitBayesianEngine()
    diag = engine.diagnostics()
    suite.assert_true("Orbit: diagnostics operational", diag.get("status") == "operational")

    # Linear escalating array
    ts = [10.0, 20.0, 30.0, 40.0, 50.0]
    
    # Target steps = 3, expected OLS trend continues ~60, 70, 80 depending on alpha smoothing weighting
    bayes_res = engine.compute_smoothed_forecast(ts, prediction_steps=3, alpha_smoothing=0.5)
    suite.assert_ok("Orbit: Calculated Bayesian Time-Series State", bayes_res)
    
    if type(bayes_res).__name__ == "Ok" or hasattr(bayes_res, "value"):
        forecasts = bayes_res.value["forecasted_horizon"]
        suite.assert_true("Orbit: Extrapolated accurately 3 forward states", len(forecasts) == 3)
        suite.assert_true("Orbit: Slope regression math mathematically follows vector (ascending)", forecasts[0] > 40.0)

    suite.assert_err("Orbit: Reject empty series arrays", engine.compute_smoothed_forecast([]))
    suite.assert_err("Orbit: Enforce smoothing factor limits", engine.compute_smoothed_forecast(ts, alpha_smoothing=9.9))

except Exception as exc:
    suite.assert_true(f"Orbit: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 5: OmniModel2VecEngine
# ===================================================================
try:
    from omni_model2vec_engine import OmniModel2VecEngine

    engine = OmniModel2VecEngine()
    diag = engine.diagnostics()
    suite.assert_true("Model2Vec: diagnostics operational", diag.get("status") == "operational")

    v1 = [1.0, 0.0, -1.0]
    v2 = [1.0, 0.0, -1.0] # perfect identical match
    
    m2v_res = engine.compute_similarity(v1, v2)
    suite.assert_ok("Model2Vec: Fast Dot quantize similarity evaluation passes", m2v_res)
    
    if type(m2v_res).__name__ == "Ok" or hasattr(m2v_res, "value"):
        val = m2v_res.value
        suite.assert_true("Model2Vec: Confirm exact identical mappings (Similarity 1.0)", val["is_identical"])
        
    # Orthogonal mapping = 0
    ortho_res = engine.compute_similarity([1.0, 0.0], [0.0, 1.0])
    if type(ortho_res).__name__ == "Ok" or hasattr(ortho_res, "value"):
        suite.assert_true("Model2Vec: Accurately maps 0.0 Cosine for true Orthogonal points", abs(ortho_res.value["absolute_cosine_similarity"]) < 0.01)

    suite.assert_err("Model2Vec: Dimension Size mismatches rejected mathematically", engine.compute_similarity([1.0], [1.0, 2.0]))

except Exception as exc:
    suite.assert_true(f"Model2Vec: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())


# ===================================================================
# PRINT RESULTS
# ===================================================================
print(suite.summary())
sys.exit(0 if all(r.passed for r in suite.results) else 1)
