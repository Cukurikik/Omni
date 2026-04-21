"""
Semester 8 Batch 17 — Integration Tests
=======================================
Validates all 5 Batch 17 engines:
  1. OmniSerenataEngine
  2. OmniJetsonEngine
  3. OmniMerlionEngine
  4. OmniCognitaEngine
  5. OmniTFProbabilityEngine
"""

import unittest
import numpy as np

from omni_serenata_engine import OmniSerenataEngine
from omni_jetson_engine import OmniJetsonEngine, ContainerManifest
from omni_merlion_engine import OmniMerlionEngine
from omni_cognita_engine import OmniCognitaEngine
from omni_tfprobability_engine import OmniTFProbabilityEngine

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

class TestSerenataEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSerenataEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_expense_outlier(self):
        engine = OmniSerenataEngine()
        detector = engine.get_detector(strictness_z=2.5) # Slight lower threshold for test
        
        # Array of 11 values, one is massively off chart
        expenses = np.array([10.5, 12.0, 9.8, 11.2, 10.0, 9.5, 11.5, 10.2, 1000.0, 10.8, 9.9])
        
        res = detector.detect_outliers(expenses)
        self.assertTrue(is_ok(res))
        
        outliers, inliers = unwrap(res)
        self.assertEqual(len(outliers), 1)
        self.assertEqual(outliers[0], 8) # index 8 is 1000.0
        self.assertEqual(len(inliers), 10)


class TestJetsonEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniJetsonEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_topological_sort(self):
        engine = OmniJetsonEngine()
        solver = engine.get_topology_solver()
        
        solver.add_container(ContainerManifest("pytorch", ["cuda", "cudnn"]))
        solver.add_container(ContainerManifest("tensorrt", ["cuda"]))
        solver.add_container(ContainerManifest("cuda", []))
        solver.add_container(ContainerManifest("cudnn", ["cuda"]))
        solver.add_container(ContainerManifest("stable-diffusion", ["pytorch", "tensorrt"]))
        
        res = solver.resolve_build_order()
        self.assertTrue(is_ok(res))
        
        seq = unwrap(res)
        self.assertEqual(len(seq), 5)
        # cuda -> cudnn -> pytorch / tensorrt -> stable-diffusion
        self.assertEqual(seq[0], "cuda")
        self.assertEqual(seq[-1], "stable-diffusion")
        self.assertTrue(seq.index("pytorch") > seq.index("cudnn"))
        self.assertTrue(seq.index("cudnn") > seq.index("cuda"))


class TestMerlionEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniMerlionEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_autoregression(self):
        engine = OmniMerlionEngine()
        forecaster = engine.get_forecaster(lags=2)
        
        # Basic Fibonacci-like logical series sum of last two elements
        # 1, 1, 2, 3, 5, 8, 13
        series = np.array([1.0, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0, 34.0, 55.0])
        
        # Fit models
        res = forecaster.fit(series)
        self.assertTrue(is_ok(res))
        
        # Test forecast
        # Last two are 34.0 and 55.0
        # Expected next: 89.0
        pred_res = forecaster.forecast(series, steps=1)
        self.assertTrue(is_ok(pred_res))
        preds = unwrap(pred_res)
        
        self.assertTrue(np.allclose(preds[0], 89.0, atol=0.1))


class TestCognitaEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniCognitaEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_rag_semantic_search(self):
        engine = OmniCognitaEngine()
        retriever = engine.get_retriever()
        
        corpus = [
            "Rust is an amazing systems language.",
            "Python is very nice for machine learning and data science.",
            "Rust ensures memory safety through a borrow checker.",
            "The capital of France is Paris."
        ]
        
        res_ingest = retriever.ingest(corpus)
        self.assertTrue(is_ok(res_ingest))
        
        # Search about memory management
        res_search = retriever.search("Tell me about memory safety and borrow checker", top_k=2)
        self.assertTrue(is_ok(res_search))
        
        results = unwrap(res_search)
        self.assertEqual(len(results), 2)
        # Should rank third sentence highest
        self.assertEqual(results[0]["document"], corpus[2])
        self.assertTrue(results[0]["score"] > 0)


class TestTFProbabilityEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTFProbabilityEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_metropolis_mcmc(self):
        engine = OmniTFProbabilityEngine()
        sampler = engine.get_sampler()
        
        # Simple target: 1D Gaussian centered at 5.0 with variance 1.0
        # Target Log Prob = -0.5 * (x - 5.0)^2
        def target_log_prob(x: np.ndarray) -> float:
            return float(-0.5 * np.sum((x - 5.0)**2))
            
        initial = np.array([0.0]) # Start far away
        res = sampler.sample(target_log_prob, initial, num_results=2000, step_size=1.0)
        
        self.assertTrue(is_ok(res))
        samples, metrics = unwrap(res)
        
        self.assertEqual(samples.shape, (2000, 1))
        
        # Discard burn-in (first 500)
        valid_samples = samples[500:]
        mean_estimate = float(np.mean(valid_samples))
        
        # The sampler should walk from 0.0 towards 5.0 and cluster there
        self.assertTrue(abs(mean_estimate - 5.0) < 0.5)
        self.assertTrue(metrics["acceptance_rate"] > 0.0)


if __name__ == "__main__":
    unittest.main()
