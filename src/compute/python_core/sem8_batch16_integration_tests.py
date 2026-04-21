"""
Semester 8 Batch 16 — Integration Tests
=======================================
Validates all 5 Batch 16 engines:
  1. OmniRathEngine
  2. OmniSDVideosEngine
  3. OmniEconMLEngine
  4. OmniTFDatasetsEngine
  5. OmniAccordNetEngine
"""

import unittest
import numpy as np

from omni_rath_engine import OmniRathEngine
from omni_sd_videos_engine import OmniSDVideosEngine
from omni_econml_engine import OmniEconMLEngine
from omni_tf_datasets_engine import OmniTFDatasetsEngine
from omni_accordnet_engine import OmniAccordNetEngine

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

class TestRathEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniRathEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_insight_walker(self):
        engine = OmniRathEngine()
        # Create dataset where feature 1 and 2 have artificially high variance
        data = np.zeros((100, 4))
        data[:, 0] = np.random.normal(0, 0.1, 100)  # low var
        data[:, 1] = np.random.normal(0, 10.0, 100) # hi var
        data[:, 2] = np.random.normal(0, 5.0, 100)  # med var
        data[:, 3] = np.random.normal(0, 0.2, 100)  # low var
        
        res = engine.analyze(data)
        self.assertTrue(is_ok(res))
        
        insight = unwrap(res)
        # Verify it chose columns 1 and 2
        choices = {insight.x_axis_index, insight.y_axis_index}
        self.assertEqual(choices, {1, 2})
        self.assertEqual(insight.visualization_type, "scatter")


class TestSDVideosEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSDVideosEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_slerp_generation(self):
        engine = OmniSDVideosEngine()
        interpolator = engine.get_interpolator()
        
        latent_a = np.array([1.0, 0.0])
        latent_b = np.array([0.0, 1.0])
        
        # SLERP should rotate smoothly 90 degrees
        res = interpolator.generate_frames(latent_a, latent_b, num_frames=3)
        self.assertTrue(is_ok(res))
        
        frames = unwrap(res)
        self.assertEqual(len(frames), 3)
        # Midpoint should be exactly at 45 degrees, i.e., [sqrt(2)/2, sqrt(2)/2] ~ [0.707, 0.707]
        np.testing.assert_almost_equal(frames[1][0], 0.70710678)
        np.testing.assert_almost_equal(frames[1][1], 0.70710678)


class TestEconMLEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniEconMLEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_dml_ate(self):
        engine = OmniEconMLEngine()
        estimator = engine.get_estimator()
        
        np.random.seed(42)
        N = 100
        # Confounders
        X = np.random.normal(0, 1, (N, 2))
        # Treatment assignment
        T = np.random.binomial(1, 0.5, N)
        # True Effect is +2.0
        Y = 2.0 * T + 1.5 * X[:, 0] + -0.5 * X[:, 1] + np.random.normal(0, 0.1, N)
        
        res = estimator.estimate_ate(Y, T, X)
        self.assertTrue(is_ok(res))
        
        ate = unwrap(res)
        self.assertTrue(abs(ate - 2.0) < 0.2) # Should reconstruct +2.0 within margin


class TestTFDatasetsEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTFDatasetsEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_lazy_pipeline(self):
        engine = OmniTFDatasetsEngine()
        builder = engine.get_builder()
        
        data = np.arange(10).reshape(-1, 1)
        labels = np.arange(10)
        
        res = builder.load(data, labels)
        self.assertTrue(is_ok(res))
        
        buffer = unwrap(res)
        # Iterator should return batches
        batches = list(buffer.stream_batches(batch_size=3, shuffle=False))
        self.assertEqual(len(batches), 4) # 3, 3, 3, 1
        
        x_last, y_last = batches[-1]
        self.assertEqual(len(x_last), 1)


class TestAccordNetEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAccordNetEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_svm_smo_training(self):
        engine = OmniAccordNetEngine()
        
        # Setup linearly separable logic (AND gate behavior +1 / -1)
        inputs = np.array([
            [1.0, 1.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [0.0, 0.0]
        ])
        outputs = np.array([1, -1, -1, -1])  # AND gate
        
        svm = engine.new_svm(dimensions=2)
        smo = engine.new_smo(svm=svm, complexity=1.0)
        
        res = smo.learn(inputs, outputs)
        self.assertTrue(is_ok(res))
        
        trained_model = unwrap(res)
        
        # Forward pass evaluations
        self.assertEqual(trained_model.decide(np.array([1.0, 1.0])), 1)
        self.assertEqual(trained_model.decide(np.array([0.0, 0.0])), -1)


if __name__ == "__main__":
    unittest.main()
