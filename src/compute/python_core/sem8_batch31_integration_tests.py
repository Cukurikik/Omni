"""
Semester 8 Batch 31 — Integration Tests
=======================================
Validates all 5 Batch 31 engines:
  1. OmniTradeMasterEngine
  2. OmniAIMETEngine
  3. OmniDeepDetectEngine
  4. OmniSupabasePyEngine
  5. OmniCausalNexEngine
"""

import unittest

from omni_trademaster_engine import OmniTradeMasterEngine
from omni_aimet_engine import OmniAIMETEngine
from omni_deepdetect_engine import OmniDeepDetectEngine
from omni_supabase_py_engine import OmniSupabasePyEngine
from omni_causalnex_engine import OmniCausalNexEngine


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

class TestTradeMasterEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTradeMasterEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_rl_alpha_decay_simulator(self):
        engine = OmniTradeMasterEngine()
        est = engine.get_estimator()
        
        res = est.evaluate_structural_trade_agent_performance(state_space_dim=100, action_space_dim=50, episodes=100)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_trading_simulated"])
        self.assertTrue(out["predicted_sharpe_ratio"] < 1.5) # Complexity decayed the return
        self.assertTrue(out["resolved_action_latency_ms"] > 0.0)


class TestAimetEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAIMETEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_quantization_entropy_compression(self):
        engine = OmniAIMETEngine()
        proj = engine.get_projector()
        
        # Test 8-bit quantization with Hexagon DSP optimization
        res = proj.evaluate_structural_compression_accuracy(base_accuracy_pct=95.0, bit_width=8, optimize_for_hexagon=True)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_quantization_simulated"])
        self.assertEqual(out["compression_ratio"], 4.0) # 32/8
        self.assertTrue(out["predicted_accuracy"] < 95.0)


class TestDeepDetectEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniDeepDetectEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_amdahl_inference_throughput(self):
        engine = OmniDeepDetectEngine()
        mapper = engine.get_mapper()
        
        # 16 Workers scaling a 50ms inference payload
        res = mapper.evaluate_structural_inference_qps(parallel_workers=16, single_inference_ms=50.0, payload_mb=2.5)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_server_simulated"])
        self.assertTrue(out["theoretical_amdahl_speedup"] > 1.0)
        self.assertTrue(out["predicted_max_qps"] > 0.0)


class TestSupabasePyEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSupabasePyEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_rpc_connection_pool_limits(self):
        engine = OmniSupabasePyEngine()
        est = engine.get_estimator()
        
        # Overloaded pool (300 active) vs calm pool (50 active)
        res_calm = est.evaluate_structural_rpc_latency(active_connections=50, query_complexity_weight=1.5, payload_kb=10.0)
        res_heavy = est.evaluate_structural_rpc_latency(active_connections=300, query_complexity_weight=1.5, payload_kb=10.0)
        
        self.assertTrue(is_ok(res_calm))
        self.assertTrue(is_ok(res_heavy))
        
        out_calm = unwrap(res_calm)
        out_heavy = unwrap(res_heavy)
        
        self.assertEqual(out_calm["pool_queue_penalty"], 1.0)
        self.assertTrue(out_heavy["pool_queue_penalty"] > 1.0)
        self.assertTrue(out_heavy["resolved_query_latency_ms"] > out_calm["resolved_query_latency_ms"])


class TestCausalNexEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniCausalNexEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_bayesian_confidence_bounds(self):
        engine = OmniCausalNexEngine()
        b_eval = engine.get_evaluator()
        
        res = b_eval.evaluate_structural_causal_confidence_bounds(node_count=10, edge_density_pct=50.0, observation_samples=500)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_dag_simulated"])
        self.assertTrue(out["predicted_inference_confidence"] > 0.5)


if __name__ == "__main__":
    unittest.main()
