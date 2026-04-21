"""
Semester 8 Batch 25 — Integration Tests
=======================================
Validates all 5 Batch 25 engines:
  1. OmniStemrollerEngine
  2. OmniImgClsMobEngine
  3. OmniTensorRTEngine
  4. OmniMITIEEngine
  5. OmniAwesomeMLSSEngine
"""

import unittest
import numpy as np

from omni_stemroller_engine import OmniStemrollerEngine
from omni_imgclsmob_engine import OmniImgClsMobEngine
from omni_tensorrt_engine import OmniTensorRTEngine
from omni_mitie_engine import OmniMITIEEngine
from omni_awesome_mlss_engine import OmniAwesomeMLSSEngine

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

class TestStemrollerEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniStemrollerEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_vocal_isolation(self):
        engine = OmniStemrollerEngine()
        sim = engine.get_simulator()
        
        # Audio bounds Mock: combination of loud (vocal) and soft (instrumental)
        audio_array = np.array([0.1, -0.2, 0.9, -0.8, 0.05, -0.1], dtype=np.float64)
        
        res = sim.separate_stems_deterministically(audio_array)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_isolated"])
        self.assertTrue(out["vocal_energy_ratio"] > 0)


class TestImgClsMobEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniImgClsMobEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_mobile_efficiency(self):
        engine = OmniImgClsMobEngine()
        evaluator = engine.get_evaluator()
        
        # MobileNetV2 approx: 3M params, 300M flops
        res = evaluator.evaluate_model_efficiency("MobileNetV2", 3_000_000, 300_000_000)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_mobile_optimized"])
        self.assertTrue(out["theoretical_mobile_fps"] > 0.0)


class TestTensorRTEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTensorRTEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_graph_node_merger(self):
        engine = OmniTensorRTEngine()
        merger = engine.get_merger()
        
        res = merger.simulate_engine_build(graph_nodes=100, is_fp16=True)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["fused_node_count"], 60) # 0.6 reduction
        self.assertTrue(out["used_half_precision"])
        self.assertTrue(out["predicted_speedup_ratio"] > 1.0)


class TestMITIEEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniMITIEEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_sentence_chunking(self):
        engine = OmniMITIEEngine()
        evaluator = engine.get_evaluator()
        
        tokens = ["The", "quick", "brown", "fox", "jumps", "in", "London"]
        res = evaluator.extract_chunks_deterministically(tokens)
        
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["entities_extracted_count"], 2) # "The", "London"
        self.assertEqual(out["entities"][1]["chunk"], "London")


class TestAwesomeMLSSEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAwesomeMLSSEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_curriculum_topology_sort(self):
        engine = OmniAwesomeMLSSEngine()
        evaluator = engine.get_evaluator()
        
        # DAG mappings
        edges = [
            ("Math", "MachineLearning"),
            ("Python", "MachineLearning"),
            ("MachineLearning", "DeepLearning")
        ]
        
        res = evaluator.evaluate_priority_bounds(edges)
        
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_dag"])
        # Deep learning should be last
        self.assertEqual(out["topological_sequence"][-1], "DeepLearning")


if __name__ == "__main__":
    unittest.main()
