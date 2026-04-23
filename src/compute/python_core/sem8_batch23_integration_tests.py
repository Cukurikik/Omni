"""
Semester 8 Batch 23 — Integration Tests
=======================================
Validates all 5 Batch 23 engines:
  1. OmniMLNotesEngine
  2. OmniLightlyEngine
  3. OmniAIEngineeringEngine
  4. OmniPolyaxonEngine
  5. OmniTVMEngine
"""

import unittest
import numpy as np

from omni_ml_notes_engine import OmniMLNotesEngine
from omni_lightly_engine import OmniLightlyEngine
from omni_ai_engineering_engine import OmniAIEngineeringEngine
from omni_polyaxon_engine import OmniPolyaxonEngine
from omni_tvm_engine import OmniTVMEngine

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

class TestMLNotesEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniMLNotesEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_gradient_descent(self):
        engine = OmniMLNotesEngine()
        val = engine.get_validator(lr=0.01)
        
        # execute x^2 where min is x=0
        res = val.evaluate_structural_quadratic_descent(start_pos=10.0, max_iterations=5000)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["converged"])
        # ensure it reached close to 0
        self.assertTrue(out["convergence_delta"] < 0.05)


class TestLightlyEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniLightlyEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_nt_xent_loss(self):
        engine = OmniLightlyEngine()
        calc = engine.get_calculator(temperature=0.5)
        
        # simulated batch embedding views (v1, v2)
        v1 = np.ones(64)
        v2 = np.ones(64) * 0.99 
        
        res = calc.evaluate_batch_loss(v1, v2)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        # pos sim should be extremely high close to 1.0
        self.assertTrue(out["positive_similarity"] > 0.95)
        self.assertTrue(out["similarity_gradient_gap"] > 0.0)
        self.assertIsNotNone(out["nt_xent_loss"])


class TestAIEngineeringEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAIEngineeringEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_pipeline_dag_gating(self):
        engine = OmniAIEngineeringEngine()
        gate = engine.get_balancer()
        
        # Ingestion tests
        res1 = gate.gate_ingestion_throughput(500, 10)
        self.assertTrue(is_ok(res1))
        self.assertEqual(unwrap(res1)["gate_status"], "APPROVED")
        
        # Deployment tests
        res2 = gate.gate_model_deployment(evaluation_score=0.85, previous_score=0.81)
        self.assertTrue(is_ok(res2))
        self.assertEqual(unwrap(res2)["gate_status"], "DEPLOYED")
        
        res3 = gate.gate_model_deployment(evaluation_score=0.75, previous_score=0.80)
        self.assertTrue(is_ok(res3))
        self.assertEqual(unwrap(res3)["gate_status"], "REJECTED")


class TestPolyaxonEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniPolyaxonEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_pod_scheduling(self):
        engine = OmniPolyaxonEngine()
        scheduler = engine.get_scheduler(max_cpu=8.0, max_ram=16.0)
        
        # Fit easily
        res1 = scheduler.schedule_experiment(req_cpu=4.0, req_ram=8.0)
        self.assertTrue(is_ok(res1))
        self.assertEqual(unwrap(res1)["status"], "SCHEDULED")
        
        # Try to schedule beyond limits
        res2 = scheduler.schedule_experiment(req_cpu=6.0, req_ram=12.0)
        self.assertTrue(is_ok(res2))
        self.assertTrue("PENDING" in unwrap(res2)["status"])
        
        # utilization should reflect the first scheduled job
        self.assertEqual(unwrap(res2)["utilization_cpu_pct"], 50.0)


class TestTVMEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTVMEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_operator_fusion(self):
        engine = OmniTVMEngine()
        fuser = engine.get_fuser()
        
        sequence = ["Conv2D", "BatchNorm", "ReLU", "Softmax"]
        
        res = fuser.evaluate_fused_latency(sequence)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["fused_blocks_created"], 1)
        self.assertTrue(out["optimization_gain_pct"] > 0.0)
        self.assertTrue(out["fused_latency_ms"] < out["unfused_latency_ms"])


if __name__ == "__main__":
    unittest.main()
