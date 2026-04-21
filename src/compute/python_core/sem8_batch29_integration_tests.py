"""
Semester 8 Batch 29 — Integration Tests
=======================================
Validates all 5 Batch 29 engines:
  1. OmniCloudAnnotationsEngine
  2. OmniVoxelmorphEngine
  3. OmniDeepCameraEngine
  4. OmniCVCUDAEngine
  5. OmniAutodistillEngine
"""

import unittest

from omni_cloudannotations_engine import OmniCloudAnnotationsEngine
from omni_voxelmorph_engine import OmniVoxelmorphEngine
from omni_deepcamera_engine import OmniDeepCameraEngine
from omni_cvcuda_engine import OmniCVCUDAEngine
from omni_autodistill_engine import OmniAutodistillEngine

# ---------------------------------------------------------------------------
# Monadic Helpers
# ---------------------------------------------------------------------------
def is_ok(result) -> bool:
    return hasattr(result, "value") and not hasattr(result, "error")

def is_err(result) -> bool:
    return hasattr(result, "error") and not hasattr(result, "value")

def unwrap(result):
    return result.value


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

class TestCloudAnnotationsEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniCloudAnnotationsEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_iou_intersection(self):
        engine = OmniCloudAnnotationsEngine()
        evaluator = engine.get_evaluator()
        
        # Perfect overlap
        res1 = evaluator.calculate_overlap_ratio((0, 0, 10, 10), (0, 0, 10, 10))
        self.assertTrue(is_ok(res1))
        out1 = unwrap(res1)
        self.assertEqual(out1["iou_ratio"], 1.0)
        self.assertTrue(out1["is_overlapping"])
        
        # No overlap
        res2 = evaluator.calculate_overlap_ratio((0, 0, 10, 10), (20, 20, 30, 30))
        self.assertTrue(is_ok(res2))
        out2 = unwrap(res2)
        self.assertEqual(out2["iou_ratio"], 0.0)
        self.assertFalse(out2["is_overlapping"])


class TestVoxelmorphEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniVoxelmorphEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_deformation_field_vector(self):
        engine = OmniVoxelmorphEngine()
        evaluator = engine.get_evaluator()
        
        res = evaluator.simulate_deformation_stress(grid_volume=128**3, shift_intensity=0.5)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_deformation_simulated"])
        self.assertTrue(out["synthetic_smoothness_loss"] > 0)
        self.assertTrue(out["deformation_field_vram_mb"] > 0)


class TestDeepCameraEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniDeepCameraEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_edge_ai_throughput(self):
        engine = OmniDeepCameraEngine()
        est = engine.get_estimator()
        
        # Single camera, low flops
        res1 = est.simulate_hardware_framerate(camera_count=1, resolution_width=1280, model_flops=5e9)
        self.assertTrue(is_ok(res1))
        out1 = unwrap(res1)
        self.assertTrue(out1["realized_edge_fps"] > 30.0)
        
        # Many cameras, high flops (should throttle heavily)
        res2 = est.simulate_hardware_framerate(camera_count=16, resolution_width=1920, model_flops=50e9)
        self.assertTrue(is_ok(res2))
        out2 = unwrap(res2)
        self.assertTrue(out2["is_edge_bounded"])


class TestCVCUDAEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniCVCUDAEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_kernel_bandwidth_latency(self):
        engine = OmniCVCUDAEngine()
        sim = engine.get_simulator()
        
        res = sim.simulate_kernel_latency(image_width=1920, image_height=1080, batch_size=32, complexity_scalar=0.8)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_memory_bound"])
        self.assertTrue(out["total_theoretical_ms"] > 0.0)


class TestAutodistillEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAutodistillEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_accuracy_retention_decay(self):
        engine = OmniAutodistillEngine()
        est = engine.get_estimator()
        
        # Huge compression: 100B parameter teacher -> 1B parameter student
        res = est.simulate_teacher_student_fidelity(teacher_params=100_000_000_000, student_params=1_000_000_000, teacher_accuracy=0.95)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_distillation_feasible"])
        self.assertTrue(out["student_predicted_accuracy"] < out["teacher_accuracy"])
        self.assertEqual(out["latency_speedup_multiplier"], 100.0)


if __name__ == "__main__":
    unittest.main()
