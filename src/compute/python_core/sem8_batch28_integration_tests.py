"""
Semester 8 Batch 28 — Integration Tests
=======================================
Validates all 5 Batch 28 engines:
  1. OmniMTBookEngine
  2. OmniMarsEngine
  3. OmniDallePlaygroundEngine
  4. OmniPOTEngine
  5. OmniUnsplashDatasetsEngine
"""

import unittest
import numpy as np

from omni_mtbook_engine import OmniMTBookEngine
from omni_mars_engine import OmniMarsEngine
from omni_dalleplayground_engine import OmniDallePlaygroundEngine
from omni_pot_engine import OmniPOTEngine
from omni_unsplashdatasets_engine import OmniUnsplashDatasetsEngine

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

class TestMTBookEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniMTBookEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_syntactic_alignment_projection(self):
        engine = OmniMTBookEngine()
        sim = engine.get_structural_evaluator()
        
        src = ["We", "have", "arrived"]
        tgt = ["Nous", "sommes", "arrivés", "ici"]
        
        res = sim.evaluate_structural_token_alignment(src, tgt)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_statically_aligned"])
        self.assertEqual(out["matrix_dimensions"], (3, 4))
        self.assertEqual(len(out["alignments"]), 3)
        self.assertTrue(out["mean_alignment_confidence"] > 0)


class TestMarsEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniMarsEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_distributed_dag_latency(self):
        engine = OmniMarsEngine()
        est = engine.get_estimator()
        
        res = est.evaluate_structural_chunk_distribution(1_000_000, cluster_nodes=5)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_distributed_topology"])
        self.assertEqual(out["nodes_active"], 5)
        self.assertTrue(out["total_estimated_latency_ms"] > 0)


class TestDallePlaygroundEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniDallePlaygroundEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_latent_diffusion_estimation(self):
        engine = OmniDallePlaygroundEngine()
        est = engine.get_estimator()
        
        res = est.evaluate_structural_diffusion_steps(inference_steps=20, base_resolution=512, cfg_scale=7.5)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["inference_steps"], 20)
        self.assertTrue(out["predicted_total_time_sec"] > 0.0)
        self.assertTrue(out["is_fidelity_converged"])


class TestPOTEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniPOTEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_wasserstein_distance_mock(self):
        engine = OmniPOTEngine()
        calc = engine.get_calculator()
        
        src = [0.1, 0.2, 0.7]
        tgt = [0.5, 0.3, 0.2]
        
        res = calc.calculate_transport_cost(src, tgt)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_transport_feasible"])
        self.assertTrue(out["wasserstein_distance"] >= 0)
        self.assertTrue(out["sinkhorn_entropy_bound"] < 0) # Log of values < 1 is negative


class TestUnsplashDatasetsEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniUnsplashDatasetsEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_metadata_extrapolation(self):
        engine = OmniUnsplashDatasetsEngine()
        clusterizer = engine.get_clusterizer()
        
        res = clusterizer.clusterize_image_proportions(row_simulation_count=200000)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["resolved_image_entries"], 200000)
        self.assertTrue(out["is_statically_resolved"])
        self.assertTrue("landscape" in out["dimension_proportions"])


if __name__ == "__main__":
    unittest.main()
