"""
Semester 8 Batch 14 — Integration Tests
=======================================
Validates all 5 Batch 14 engines:
  1. OmniPyTorchForecastingEngine
  2. OmniArgillaEngine
  3. OmniChronosEngine
  4. OmniMegEngine
  5. OmniISREngine

All operations are zero-algebraic_bound using pure python/NumPy.
"""

import unittest
import numpy as np

from omni_pytorch_forecasting_engine import OmniPyTorchForecastingEngine
from omni_argilla_engine import OmniArgillaEngine, TextClassificationRecord, PreferenceRecord, ArgillaDataset
from omni_chronos_engine import OmniChronosEngine
from omni_megengine_engine import OmniMegEngine
from omni_isr_engine import OmniISREngine

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

class TestPyTorchForecastingEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniPyTorchForecastingEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_exponential_smoothing_forecast(self):
        engine = OmniPyTorchForecastingEngine()
        data = np.array([10, 12, 14, 16, 18, 20])  # Clear linear trend
        time = np.array([1, 2, 3, 4, 5, 6])
        
        ds_res = engine.create_dataset(data, time, target="value")
        self.assertTrue(is_ok(ds_res))
        
        model = engine.create_model()
        fit_res = model.fit(unwrap(ds_res))
        self.assertTrue(is_ok(fit_res))
        
        pred_res = model.predict(steps=3)
        self.assertTrue(is_ok(pred_res))
        
        predictions = unwrap(pred_res)
        self.assertEqual(len(predictions), 3)
        # Should continue the upward trend
        self.assertGreater(predictions[0], 20)
        self.assertGreater(predictions[1], predictions[0])


class TestArgillaEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniArgillaEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_reward_modeling_rlhf(self):
        engine = OmniArgillaEngine()
        dataset = ArgillaDataset("rlhf_test")
        
        # Add classification
        cls_rec = TextClassificationRecord(text="Great product", prediction=[("positive", 0.9)])
        dataset.add_classification(cls_rec)
        
        # Add preferences
        dataset.add_preference(PreferenceRecord("Fix this code", "A bad fix", "A good fix", preferred="B"))
        dataset.add_preference(PreferenceRecord("Optimize this", "Speedy", "Slow", preferred="A"))
        dataset.add_preference(PreferenceRecord("Format", "Tie", "Tie", preferred=None))
        
        res = engine.log_dataset(dataset)
        self.assertTrue(is_ok(res))
        
        reward_model = engine.get_reward_model()
        metrics_res = reward_model.compute_win_rate(dataset)
        self.assertTrue(is_ok(metrics_res))
        
        metrics = unwrap(metrics_res)
        self.assertEqual(metrics["win_rate_a"], 0.333)
        self.assertEqual(metrics["win_rate_b"], 0.333)
        self.assertEqual(metrics["ties"], 1)


class TestChronosEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniChronosEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_ast_bug_detection(self):
        engine = OmniChronosEngine()
        debugger = engine.get_debugger()
        
        bad_code = """
def my_func(a, lst=[]):
    try:
        if a == True:
            lst.append(a)
    except:
        pass
        """
        
        res = debugger.analyze_source(bad_code)
        self.assertTrue(is_ok(res))
        bugs = unwrap(res)
        
        issue_types = [bug.issue_type for bug in bugs]
        self.assertIn("MutableDefaultArgument", issue_types)
        self.assertIn("BooleanEquality", issue_types)
        self.assertIn("BareExcept", issue_types)


class TestMegEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniMegEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_autograd_tensor(self):
        engine = OmniMegEngine()
        
        res_a = engine.create_tensor([2.0], requires_grad=True)
        res_b = engine.create_tensor([3.0], requires_grad=True)
        self.assertTrue(is_ok(res_a) and is_ok(res_b))
        
        a = unwrap(res_a)
        b = unwrap(res_b)
        
        # c = a * b + b
        # dc/da = b (3)
        # dc/db = a + 1 (3)
        c = (a * b) + b
        c.backward()
        
        self.assertEqual(float(a.grad[0]), 3.0)
        self.assertEqual(float(b.grad[0]), 3.0)
        
        # Test ReLU
        d = engine.create_tensor([-5.0], requires_grad=True).value
        e = d.relu()
        e.backward()
        # ReLU of -5 is 0, grad is 0
        self.assertEqual(float(d.grad[0]), 0.0)


class TestISREngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniISREngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_convolutional_upscaler(self):
        engine = OmniISREngine()
        upscaler = engine.get_upscaler(scale_factor=2)
        
        # 3x3 grayscale image
        img = np.array([
            [10, 20, 30],
            [40, 50, 60],
            [70, 80, 90]
        ], dtype=np.uint8)
        
        res = upscaler.upscale(img)
        self.assertTrue(is_ok(res))
        
        upscaled = unwrap(res)
        self.assertEqual(upscaled.shape, (6, 6)) # 3*2, 3*2
        
        # 3D image
        img_3d = np.zeros((2, 2, 3), dtype=np.uint8)
        img_3d[0, 0, :] = 255
        res_3d = upscaler.upscale(img_3d)
        self.assertTrue(is_ok(res_3d))
        self.assertEqual(unwrap(res_3d).shape, (4, 4, 3))


if __name__ == "__main__":
    unittest.main()
