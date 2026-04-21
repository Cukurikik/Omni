"""
Semester 8 Batch 27 — Integration Tests
=======================================
Validates all 4 Batch 27 engines:
  1. OmniDeepnoteEngine
  2. OmniSimpleTunerEngine
  3. OmniInteractiveToolsEngine
  4. OmniGerevEngine
"""

import unittest
import numpy as np

from omni_deepnote_engine import OmniDeepnoteEngine
from omni_simpletuner_engine import OmniSimpleTunerEngine
from omni_interactive_tools_engine import OmniInteractiveToolsEngine
from omni_gerev_engine import OmniGerevEngine

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

class TestDeepnoteEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniDeepnoteEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_notebook_dag_simulation(self):
        engine = OmniDeepnoteEngine()
        sim = engine.get_simulator()
        
        # Simulated complexity load blocks
        res = sim.simulate_cellular_run([2, 5, 1])
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["cells_executed"], 3)
        self.assertTrue(out["is_dag_acyclic"])
        self.assertTrue(out["total_cycle_time_ms"] > 0)


class TestSimpleTunerEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSimpleTunerEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_vram_estimation(self):
        engine = OmniSimpleTunerEngine()
        est = engine.get_estimator()
        
        # Standard SDXL finetune parameters
        res = est.calculate_tuning_memory_footprint(1024, 1024, batch_size=2, is_sdxl=True)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_deterministic_bound"])
        self.assertEqual(out["base_model_vram_gb"], 5.6)
        self.assertTrue(out["total_estimated_vram_gb"] > 10.0)


class TestInteractiveToolsEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniInteractiveToolsEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_gradient_visual_convergence(self):
        engine = OmniInteractiveToolsEngine()
        mapper = engine.get_mapper()
        
        # Start loss 1.5, LR 0.05, 50 epochs
        res = mapper.simulate_visual_descent(1.5, 0.05, 50)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["epochs_simulated"], 50)
        self.assertTrue(out["convergence_ratio"] > 0.0)
        self.assertTrue(out["loss_trajectory_variance"] > 0.0)


class TestGerevEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniGerevEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_enterprise_semantic_retrieval(self):
        engine = OmniGerevEngine()
        retriever = engine.get_retriever()
        
        docs = [
            "We have no data on user payments.",
            "Enterprise authentication protocols require SSL certs.",
            "The quick search algorithm retrieves user payment data well."
        ]
        
        res = retriever.simulate_semantic_retrieval("user payments", docs)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_search_resolved"])
        self.assertEqual(out["documents_scanned"], 3)
        self.assertEqual(out["best_match_index"], 0)


if __name__ == "__main__":
    unittest.main()
