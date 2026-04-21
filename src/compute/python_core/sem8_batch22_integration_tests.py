"""
Semester 8 Batch 22 — Integration Tests
=======================================
Validates all 5 Batch 22 engines:
  1. OmniTFOnSparkEngine
  2. OmniTurbopilotEngine
  3. OmniSwanMonitorEngine
  4. OmniFinancialMetricsEngine
  5. OmniOliviaEngine
"""

import unittest
import numpy as np

from omni_tf_on_spark_engine import OmniTFOnSparkEngine
from omni_turbopilot_engine import OmniTurbopilotEngine
from omni_swan_monitor_engine import OmniSwanMonitorEngine
from omni_financial_metrics_engine import OmniFinancialMetricsEngine
from omni_olivia_engine import OmniOliviaEngine

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

class TestTFOnSparkEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTFOnSparkEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_partition_balancer(self):
        engine = OmniTFOnSparkEngine()
        balancer = engine.init_balancer(num_executors=4)
        
        data = np.arange(10, dtype=np.float64) # 10 elements
        # 10 / 4 executors = sizes [3, 3, 2, 2]
        
        res = balancer.simulate_map_reduce_reduction(data, map_factor=2.0)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        # Original sum(0..9) = 45. Mapped = 45 * 2.0 = 90.0
        self.assertEqual(out["global_state"], 90.0)
        self.assertEqual(len(out["executor_payloads"]), 4)


class TestTurbopilotEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTurbopilotEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_completion_prefix(self):
        engine = OmniTurbopilotEngine()
        completer = engine.get_completer()
        
        snippets = [
            "def calculate_total(a, b): return a + b",
            "class ServerProtocol: pass",
            "import os, sys",
        ]
        
        res_seed = completer.seed_completion_corpus(snippets)
        self.assertTrue(is_ok(res_seed))
        
        res_gen = completer.generate_completion("def calc")
        self.assertTrue(is_ok(res_gen))
        out = unwrap(res_gen)
        # Should match the calculate snippet based on Jaccard bigrams/trigrams
        self.assertTrue("calculate_total" in out["suggestion"])


class TestSwanMonitorEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSwanMonitorEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_differential_stabilization(self):
        engine = OmniSwanMonitorEngine()
        tracker = engine.get_tracker()
        
        # Simulate loss dropping and then stabilizing
        tracker.log_metric("loss", 1.0)
        tracker.log_metric("loss", 0.5)
        tracker.log_metric("loss", 0.2)
        tracker.log_metric("loss", 0.1)
        tracker.log_metric("loss", 0.101)
        tracker.log_metric("loss", 0.099)
        
        res = tracker.evaluate_stabilization("loss", window=3)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_stable"])
        self.assertTrue(out["velocity"] < 0.05)


class TestFinancialMetricsEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniFinancialMetricsEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_amortization_schedule(self):
        engine = OmniFinancialMetricsEngine()
        calc = engine.get_calculus()
        
        res = calc.compute_schedule(principal=100000, annual_rate=0.05, years=1)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["tensor_schedule_shape"], (12, 3))
        # Total interest paid mathematically should be > 0
        self.assertTrue(out["total_interest_paid"] > 0)


class TestOliviaEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniOliviaEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_intent_matching(self):
        engine = OmniOliviaEngine()
        matcher = engine.get_matcher()
        
        matcher.register_intent_hash("GREETING", ["hello", "hi there", "greetings friend"])
        matcher.register_intent_hash("WEATHER", ["whats the weather", "is it raining weather today"])
        
        res = matcher.predict_intent("hello friend")
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["intent"], "GREETING")
        self.assertTrue(out["confidence_bounds"] > 0.0)
        

if __name__ == "__main__":
    unittest.main()
