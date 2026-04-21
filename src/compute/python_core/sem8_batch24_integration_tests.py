"""
Semester 8 Batch 24 — Integration Tests
=======================================
Validates all 5 Batch 24 engines:
  1. OmniDeepVariantEngine
  2. OmniPennyLaneAIEngine
  3. OmniOpenVINOEngine
  4. OmniLiteratureDLEngine
  5. OmniHDBSCANEngine
"""

import unittest
import math
import numpy as np

from omni_deepvariant_engine import OmniDeepVariantEngine
from omni_pennylane_ai_engine import OmniPennyLaneAIEngine
from omni_openvino_engine import OmniOpenVINOEngine
from omni_literature_dl_engine import OmniLiteratureDLEngine
from omni_hdbscan_engine import OmniHDBSCANEngine

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

class TestDeepVariantEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniDeepVariantEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_allele_probability(self):
        engine = OmniDeepVariantEngine()
        val = engine.get_simulator()
        
        ref = "A"
        # 4 A's, 1 T -> possible error or Het
        reads = ["A", "A", "A", "A", "T"]
        
        res = val.evaluate_genotype_likelihood(ref, reads)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue("variant_call" in out)
        self.assertTrue(out["phred_quality_score"] > 0)


class TestPennyLaneAIEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniPennyLaneAIEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_quantum_rotation(self):
        engine = OmniPennyLaneAIEngine()
        circuit = engine.get_circuit_modifier(num_qubits=2)
        
        res_rot = circuit.apply_rx_rotation(0, math.pi / 2.0)
        self.assertTrue(is_ok(res_rot))
        
        res_expect = circuit.measure_expectation_z()
        self.assertTrue(is_ok(res_expect))
        out = unwrap(res_expect)
        
        # Q0 rotated pi/2 -> expectation cos(pi/2) ~ 0
        # Q1 not rotated -> expectation 1
        # average -> roughly 0.5
        score = out["overall_z_expectation"]
        self.assertTrue(0.4 < score < 0.6)


class TestOpenVINOEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniOpenVINOEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_quantization_latency(self):
        engine = OmniOpenVINOEngine()
        sim = engine.get_simulator()
        
        res_fp32 = sim.simulate_quantized_inference(num_parameters_millions=5.0, is_int8=False)
        self.assertTrue(is_ok(res_fp32))
        ms_fp32 = unwrap(res_fp32)["latency_ms"]
        
        res_int8 = sim.simulate_quantized_inference(num_parameters_millions=5.0, is_int8=True)
        self.assertTrue(is_ok(res_int8))
        ms_int8 = unwrap(res_int8)["latency_ms"]
        
        self.assertTrue(ms_int8 < ms_fp32)
        self.assertTrue(unwrap(res_int8)["is_quantized"])


class TestLiteratureDLEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniLiteratureDLEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_clustering_coefficient(self):
        engine = OmniLiteratureDLEngine()
        calc = engine.get_calculator()
        
        # Triangle graph: 0-1, 1-2, 2-0 = perfect score 1.0 clustering
        edges = [(0, 1), (1, 2), (2, 0)]
        
        res = calc.evaluate_graph_structure(num_nodes=3, edges=edges)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["average_clustering_score"], 1.0)
        self.assertTrue(out["is_densely_connected"])


class TestHDBSCANEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniHDBSCANEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_density_core_distance(self):
        engine = OmniHDBSCANEngine()
        sim = engine.get_simulator()
        
        spatial_data = np.array([
            [1.0, 1.0], [1.1, 1.1], [0.9, 1.0], [1.0, 0.9],
            [10.0, 10.0] # far outlier
        ], dtype=np.float64)
        
        res = sim.evaluate_core_distances(spatial_data, min_samples=3)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["mean_core_distance"] > 0)
        self.assertTrue(out["max_core_distance_bound"] > out["min_core_distance_bound"])


if __name__ == "__main__":
    unittest.main()
