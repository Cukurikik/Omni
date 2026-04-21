"""
Semester 8 Batch 18 — Integration Tests
=======================================
Validates all 5 Batch 18 engines:
  1. OmniWatermarkEngine
  2. OmniISLREngine
  3. OmniSacredEngine
  4. OmniAdPapersEngine
  5. OmniNeuroEngine
"""

import unittest
import numpy as np

from omni_watermark_engine import OmniWatermarkEngine
from omni_islr_engine import OmniISLREngine
from omni_sacred_engine import OmniSacredEngine
from omni_adpapers_engine import OmniAdPapersEngine
from omni_neuro_engine import OmniNeuroEngine

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

class TestWatermarkEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniWatermarkEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_morphological_inpainting(self):
        engine = OmniWatermarkEngine()
        inpainter = engine.get_inpainter(max_iter=10) # light test
        
        # 5x5 image of pure 10.0 intensity
        image = np.full((5, 5), 10.0)
        # Apply a "damaged" watermark line of 0.0 down the middle
        image[:, 2] = 0.0
        
        # Mask where the damage is
        mask = np.zeros((5, 5), dtype=bool)
        mask[:, 2] = True
        
        res = inpainter.restore(image, mask)
        self.assertTrue(is_ok(res))
        
        restored = unwrap(res)
        # Should have bled the 10.0 inwards, filling the gap
        self.assertTrue(np.all(restored[:, 2] > 0.0))
        # Top-left should remain 10.0 untouched
        self.assertEqual(restored[0, 0], 10.0)


class TestISLREngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniISLREngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_ridge_regression(self):
        engine = OmniISLREngine()
        # High penalty
        model = engine.get_model(l2_penalty=0.1)
        
        # y = 2x1 + 3x2 + 5 (noise-free)
        X = np.array([
            [1.0, 2.0],
            [2.0, 1.0],
            [3.0, 3.0],
            [1.0, 1.0]
        ])
        y = np.array([13.0, 12.0, 20.0, 10.0])
        
        res_fit = model.fit(X, y)
        self.assertTrue(is_ok(res_fit))
        
        X_test = np.array([[2.0, 2.0]])
        # expected: 5 + 2(2) + 3(2) = 15
        res_pred = model.predict(X_test)
        self.assertTrue(is_ok(res_pred))
        
        pred = unwrap(res_pred)
        self.assertTrue(abs(pred[0] - 15.0) < 1.0) # Within L2 margin bound


class TestSacredEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSacredEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_experiment_telemetry(self):
        engine = OmniSacredEngine()
        obs = engine.init_observer("test_run")
        
        self.assertTrue(is_ok(obs.inherit_config({"learning_rate": 0.01})))
        self.assertTrue(is_ok(obs.log_metric("loss", 0.5)))
        self.assertTrue(is_ok(obs.log_metric("loss", 0.3)))
        
        res = obs.conclude()
        self.assertTrue(is_ok(res))
        record = unwrap(res)
        
        self.assertEqual(record.status, "COMPLETED")
        self.assertEqual(record.config["learning_rate"], 0.01)
        self.assertEqual(len(record.metrics["loss"]), 2)
        # test state bounds, cannot log after conclusion
        self.assertTrue(is_err(obs.log_metric("loss", 0.1)))


class TestAdPapersEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAdPapersEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_factorization_machine(self):
        engine = OmniAdPapersEngine()
        # Small learning problem
        fm = engine.get_ctr_model(latent_dim=2)
        
        # Very simple XOR-like problem mapping 3 features
        # 0 0 1 -> 0
        # 0 1 1 -> 1
        # 1 0 1 -> 1
        # 1 1 1 -> 0
        X = np.array([
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0]
        ])
        y = np.array([0, 1, 1, 0])
        
        # Fit 500 epochs to force some separation pattern learning
        res_fit = fm.fit(X, y, epochs=500)
        self.assertTrue(is_ok(res_fit))
        
        res_pred = fm.predict(X)
        self.assertTrue(is_ok(res_pred))
        
        preds = unwrap(res_pred)
        self.assertEqual(len(preds), 4)
        # preds should be somewhat grouped matching the truth classes


class TestNeuroEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniNeuroEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_q_learning(self):
        engine = OmniNeuroEngine()
        agent = engine.spawn_agent(state_dim=3, action_dim=2)
        
        # State 0 -> take action 1 to get reward +5 and land in state 1
        # Test just the propagation update
        res_learn = agent.learn(state=0, action=1, reward=5.0, next_state=1)
        self.assertTrue(is_ok(res_learn))
        
        # Q(0,1) should increase
        q_value = agent.q_table[0, 1]
        self.assertTrue(q_value > 0.0)
        
        # If in State 0, exploit (epsilon 0.0) should select action 1
        res_act = agent.act(state=0, epsilon=0.0)
        self.assertTrue(is_ok(res_act))
        self.assertEqual(unwrap(res_act), 1)


if __name__ == "__main__":
    unittest.main()
