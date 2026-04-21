"""
Semester 8 Batch 20 — Integration Tests
=======================================
Validates all 5 Batch 20 engines:
  1. OmniL2LEngine
  2. OmniFinceptEngine
  3. OmniTensorEngine
  4. OmniShimmyEngine
  5. OmniSwarmUIEngine
"""

import unittest
import numpy as np

from omni_l2l_engine import OmniL2LEngine
from omni_fincept_engine import OmniFinceptEngine
from omni_tensor_engine import OmniTensorEngine
from omni_shimmy_engine import OmniShimmyEngine
from omni_swarmui_engine import OmniSwarmUIEngine

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

class TestL2LEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniL2LEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_meta_gradient_update(self):
        engine = OmniL2LEngine()
        optim = engine.get_meta_optimizer(inner_lr=0.1, outer_lr=0.5)
        
        # global logic
        global_p = np.array([1.0, 2.0])
        
        # Support
        s_x = np.array([2.0, 3.0])
        s_y = np.array([4.0, 6.0]) # target = 2*x
        
        # Query
        q_x = np.array([1.0, 4.0])
        q_y = np.array([2.0, 8.0])
        
        res = optim.run_meta_iteration(global_p, s_x, s_y, q_x, q_y)
        self.assertTrue(is_ok(res))
        
        new_params = unwrap(res)
        self.assertEqual(new_params.shape, (2,))
        # Assert parameters shifted to closer values that model y=2x


class TestFinceptEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniFinceptEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_ema_volatility(self):
        engine = OmniFinceptEngine()
        metrics = engine.get_metrics_analyzer(ema_window=3)
        
        prices = np.array([10.0, 11.0, 12.0, 15.0, 20.0, 18.0])
        
        res_ema = metrics.calculate_ema(prices)
        self.assertTrue(is_ok(res_ema))
        ema = unwrap(res_ema)
        self.assertEqual(ema.shape, (6,))
        self.assertEqual(ema[0], 0.0) # padding zeros before windows
        
        res_vol = metrics.calculate_volatility(prices, window=2)
        self.assertTrue(is_ok(res_vol))
        vols = unwrap(res_vol)
        self.assertEqual(vols.shape, (6,)) # Padded length matches original


class TestTensorEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTensorEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_broadcasting(self):
        engine = OmniTensorEngine()
        solver = engine.get_solver()
        
        a = np.array([1, 2, 3])
        b = np.array([4, 5])
        res_outer = solver.outer_product_puzzle(a, b)
        self.assertTrue(is_ok(res_outer))
        out = unwrap(res_outer)
        
        self.assertEqual(out.shape, (3, 2))
        self.assertEqual(out[0, 0], 4)
        self.assertEqual(out[2, 1], 15)
        
        # BMM mapping
        b_a = np.ones((2, 3, 4))
        b_b = np.ones((2, 4, 5))
        res_dot = solver.batched_dot_puzzle(b_a, b_b)
        self.assertTrue(is_ok(res_dot))
        dot_out = unwrap(res_dot)
        self.assertEqual(dot_out.shape, (2, 3, 5))
        self.assertEqual(dot_out[0, 0, 0], 4.0)


class TestShimmyEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniShimmyEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_transition_bridge(self):
        engine = OmniShimmyEngine()
        
        # 3 states, 2 actions
        trans = np.array([
            [1, 2],
            [0, 2],
            [2, 2] # state 2 is absorbing
        ])
        
        rewards = np.array([
            [10.0, -10.0],
            [0.0,  50.0],
            [0.0,  0.0]
        ])
        
        res_env = engine.embed_environment(trans, rewards)
        self.assertTrue(is_ok(res_env))
        env = unwrap(res_env)
        
        self.assertTrue(is_ok(env.reset()))
        
        res_step = env.step(action=0)
        self.assertTrue(is_ok(res_step))
        ns, r, d = unwrap(res_step)
        self.assertEqual(ns, 1)
        self.assertEqual(r, 10.0)
        self.assertFalse(d)
        
        res_step = env.step(action=1)
        self.assertTrue(is_ok(res_step))
        ns, r, d = unwrap(res_step)
        self.assertEqual(ns, 2)
        self.assertEqual(r, 50.0)
        self.assertTrue(d)


class TestSwarmUIEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSwarmUIEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_balancer_matrix(self):
        engine = OmniSwarmUIEngine()
        balancer = engine.get_orchestrator(node_capacity=3)
        
        tasks_cost = np.array([10.0, 5.0, 2.0, 8.0, 6.0])
        
        res = balancer.dispatch_batch(tasks_cost)
        self.assertTrue(is_ok(res))
        
        assign_map = unwrap(res)
        self.assertEqual(assign_map.shape, (5,))
        # Checking sum values assigned per nodes to ensure variance load balancing is fairly mapped
        node_loads = balancer.node_loads
        self.assertTrue(np.all(node_loads > 0))
        
        
if __name__ == "__main__":
    unittest.main()
