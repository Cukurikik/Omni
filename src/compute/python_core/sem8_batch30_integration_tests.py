"""
Semester 8 Batch 30 — Integration Tests
=======================================
Validates all 5 Batch 30 engines:
  1. OmniHoraEngine
  2. OmniOpenInterfaceEngine
  3. OmniSecretFlowEngine
  4. OmniAwesomeAIEngine
  5. OmniTimeLLMEngine
"""

import unittest

from omni_hora_engine import OmniHoraEngine
from omni_openinterface_engine import OmniOpenInterfaceEngine
from omni_secretflow_engine import OmniSecretFlowEngine
from omni_awesomeai_engine import OmniAwesomeAIEngine
from omni_timellm_engine import OmniTimeLLMEngine


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

class TestHoraEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniHoraEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_ann_latency_simulator(self):
        engine = OmniHoraEngine()
        est = engine.get_estimator()
        
        # Huge DB: 10 Million points, 768 dimensions (like BERT)
        res = est.evaluate_structural_ann_query(database_size=10_000_000, vector_dimension=768, top_k=10)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_search_simulated"])
        self.assertTrue(out["predicted_speedup_vs_exact"] > 10.0) # HNSW should be way faster than exact


class TestOpenInterfaceEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniOpenInterfaceEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_spatial_click_accuracy(self):
        engine = OmniOpenInterfaceEngine()
        pred = engine.get_predictor()
        
        # Crowded 1080p screen, very small target area
        res = pred.evaluate_structural_click_accuracy(dom_element_count=5000, target_area_pixels=100, screen_area_pixels=1920*1080)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["predicted_click_success_rate"] < 0.99)
        self.assertTrue(out["is_macro_simulated"])


class TestSecretFlowEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSecretFlowEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_cryptographic_mpc_latency(self):
        engine = OmniSecretFlowEngine()
        est = engine.get_estimator()
        
        # 10ms operation over 3 parties using SPDZ
        res = est.evaluate_structural_mpc_overhead(plaintext_compute_ms=10.0, total_parties=3, protocol="SPDZ")
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["total_parties"], 3)
        self.assertTrue(out["total_secure_latency_ms"] > 10.0)
        self.assertTrue(out["is_operation_secure"])


class TestAwesomeAIEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAwesomeAIEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_synthetic_catalog_density(self):
        engine = OmniAwesomeAIEngine()
        alloc = engine.get_allocator()
        
        res1 = alloc.generate_density_distribution("Machine Learning Core", 1_000_000)
        self.assertTrue(is_ok(res1))
        out1 = unwrap(res1)
        
        res2 = alloc.generate_density_distribution("Machine Learning Core", 1_000_000)
        self.assertTrue(is_ok(res2))
        out2 = unwrap(res2)
        
        # Ensure determinism via hash check
        self.assertEqual(out1["synthetic_project_count"], out2["synthetic_project_count"])


class TestTimeLLMEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTimeLLMEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_transformer_temporal_bounds(self):
        engine = OmniTimeLLMEngine()
        pred = engine.get_predictor()
        
        # 7B param LLM, 1024 context, 100 forecast points
        res = pred.evaluate_structural_llm_time_accuracy(historical_context_length=1024, forecast_horizon=100, llm_parameters=7_000_000_000)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["synthetic_time_mse"] > 0.0)
        self.assertTrue(out["forecast_to_context_ratio"] < 1.0)
        self.assertTrue(out["is_generation_deterministic"])


if __name__ == "__main__":
    unittest.main()
