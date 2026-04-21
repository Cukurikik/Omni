import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core')))

from omni_clear_mlops_engine import OmniClearMlOpsEngine
from omni_ml5_web_engine import OmniMl5WebEngine
from omni_daily_cv_engine import OmniDailyCvEngine
from omni_nyu_dl_engine import OmniNyuDlEngine
from omni_flappy_dqn_engine import OmniFlappyDqnEngine

class TestClearMlOpsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniClearMlOpsEngine()

    def test_pipeline_dag_simulation(self):
        self.engine.define_pipeline_node("A", [])
        self.engine.define_pipeline_node("B", ["A"])
        self.engine.define_pipeline_node("C", ["A"])
        self.engine.define_pipeline_node("D", ["B", "C"])
        
        res = self.engine.evaluate_structural_pipeline_execution()
        self.assertTrue(res.is_ok)
        order = res.unwrap()["execution_order"]
        # Expected order (A must be first, D must be last)
        self.assertEqual(order[0], "A")
        self.assertEqual(order[-1], "D")

    def test_task_logging(self):
        self.engine.init_task("Proj", "Exp1")
        self.engine.connect_hyperparameters({"lr": 0.01})
        self.engine.log_scalar("Loss", "Train", 0.5, 1)
        res = self.engine.close_task()
        self.assertTrue(res.is_ok)
        self.assertEqual(res.unwrap()["status"], "closed")

class TestMl5WebEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniMl5WebEngine()

    def test_training_pipeline(self):
        # XOR problem roughly
        self.engine.add_data([0, 0], 0)
        self.engine.add_data([0, 1], 1)
        self.engine.add_data([1, 0], 1)
        self.engine.add_data([1, 1], 0)
        
        # We don't necessarily have to normalize binary discrete inputs, but we test the module
        self.engine.normalize_data()
        
        train_res = self.engine.train(epochs=100, learning_rate=0.5, hidden_units=4)
        self.assertTrue(train_res.is_ok)
        
        cls_res = self.engine.classify([0, 1])
        self.assertTrue(cls_res.is_ok)
        label = cls_res.unwrap()["label"]
        self.assertIn(label, [0, 1])

class TestDailyCvEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniDailyCvEngine(image_size=16, patch_size=4, in_channels=3, embed_dim=16)

    def test_patch_embedding(self):
        # B, C, H, W
        x = np.random.randn(2, 3, 16, 16).astype(np.float32)
        res = self.engine.patch_embedding(x)
        self.assertTrue(res.is_ok)
        emb = res.unwrap()
        # Num patches = (16/4)**2 = 16. Plus CLS token = 17
        self.assertEqual(emb.shape, (2, 17, 16))

    def test_mhsa(self):
        # B, N+1, D
        x = np.random.randn(2, 17, 16).astype(np.float32)
        res = self.engine.multi_head_self_attention(x, num_heads=4)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        self.assertEqual(out["attention_output"].shape, (2, 17, 16))
        self.assertEqual(out["attention_weights"].shape, (2, 4, 17, 17))

class TestNyuDlEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniNyuDlEngine(in_features=5, hidden_features=10)

    def test_energy_forward(self):
        x = np.random.randn(4, 5).astype(np.float32)
        res = self.engine.energy_function_forward(x)
        self.assertTrue(res.is_ok)
        self.assertEqual(res.unwrap()["energy"].shape, (4, 1))

    def test_langevin_dynamics(self):
        x_init = np.random.randn(4, 5).astype(np.float32)
        res = self.engine.langevin_dynamics_sample(x_init, num_steps=10)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        self.assertEqual(out["sampled_x"].shape, (4, 5))
        self.assertEqual(len(out["energy_history"]), 10)

class TestFlappyDqnEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniFlappyDqnEngine(state_dim=4, action_dim=2)

    def test_dqn_pipeline(self):
        # Store topological_anchor transitions (state, action, reward, next_state, done)
        for i in range(50):
            s = np.random.randn(4).tolist()
            ns = np.random.randn(4).tolist()
            res = self.engine.store_transition(s, i % 2, 1.0, ns, False)
            self.assertTrue(res.is_ok)
            
        opt_res = self.engine.optimize_step(batch_size=16)
        self.assertTrue(opt_res.is_ok)
        self.assertIn("loss", opt_res.unwrap())
        
        act_res = self.engine.choose_action([0.0, 0.0, 0.0, 0.0], epsilon=0.0)
        self.assertTrue(act_res.is_ok)
        self.assertIn(act_res.unwrap(), [0, 1])

if __name__ == '__main__':
    unittest.main()
