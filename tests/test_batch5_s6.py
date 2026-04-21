import unittest
import numpy as np
import sys
import os

# Add the src/compute/python_core directory to the path so we can import the engines
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core')))

from omni_auto_claude_research_engine import OmniAutoClaudeResearchEngine, AgentState, AgentAction
from omni_paddle_models_engine import OmniPaddleModelsEngine
from omni_multimodal_fusion_engine import OmniMultimodalFusionEngine
from omni_federated_learning_engine import OmniFederatedLearningEngine
from omni_practical_ai_engine import OmniPracticalAiEngine

class TestAutoClaudeResearchEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniAutoClaudeResearchEngine(gamma=0.9, theta=1e-4)

    def test_optimization_loop(self):
        res = self.engine.optimize_policy()
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        self.assertIn("iterations", val)
        self.assertIn("V", val)
        self.assertIn("policy", val)
        # Check that the policy leads towards Validating -> Sleeping
        self.assertGreater(val["V"][AgentState.VALIDATE.value], 0)

    def test_simulation(self):
        res = self.engine.simulate_workflow(steps=5)
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        self.assertEqual(len(val["history"]), 5)
        self.assertIsInstance(float(val["total_reward"]), float)

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")


class TestPaddleModelsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniPaddleModelsEngine()

    def test_deformable_conv(self):
        # batch, in_c, h, w
        x = np.ones((2, 3, 4, 4), dtype=np.float32)
        # out_c, in_c, kH, kW
        w = np.ones((2, 3, 3, 3), dtype=np.float32)
        # batch, 2*kH*kW, h, w
        offsets = np.zeros((2, 18, 4, 4), dtype=np.float32)
        
        res = self.engine.deformable_conv2d(x, w, offsets, stride=1, padding=1)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        self.assertEqual(out.shape, (2, 2, 4, 4))
        # With ones everywhere and 0 offsets, output should be positive everywhere
        self.assertTrue((out > 0).all())

    def test_se_block(self):
        x = np.random.randn(2, 4, 8, 8).astype(np.float32)
        res = self.engine.squeeze_and_excitation(x, reduction=2)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        self.assertEqual(out.shape, (2, 4, 8, 8))

    def test_pp_unified_block(self):
        x = np.random.randn(2, 4, 8, 8).astype(np.float32)
        res = self.engine.pp_unified_block(x)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        self.assertEqual(out.shape, (2, 4, 8, 8))


class TestMultimodalFusionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniMultimodalFusionEngine()

    def test_cross_modal_attention(self):
        # b, seq, dim
        mod_a = np.random.randn(2, 5, 8).astype(np.float32)
        mod_b = np.random.randn(2, 10, 8).astype(np.float32)
        
        res = self.engine.cross_modal_attention(mod_a, mod_b, d_k=8)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        self.assertEqual(out["context"].shape, (2, 5, 8))
        self.assertEqual(out["attention_weights"].shape, (2, 5, 10))

    def test_tensor_fusion_network(self):
        t_feat = np.ones((2, 4), dtype=np.float32)
        v_feat = np.ones((2, 5), dtype=np.float32)
        
        res = self.engine.tensor_fusion_network(t_feat, v_feat)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        # Flattened shape: (d_text+1)*(d_visual+1) = 5 * 6 = 30
        self.assertEqual(out.shape, (2, 30))

    def test_fusion_pipeline(self):
        mod_a = np.random.randn(2, 5, 8).astype(np.float32)
        mod_b = np.random.randn(2, 10, 8).astype(np.float32)
        res = self.engine.execute_fusion_pipeline(mod_a, mod_b)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        # Output dim = (8+1)*(8+1) = 81
        self.assertEqual(out["fused_output"].shape, (2, 81))


class TestFederatedLearningEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniFederatedLearningEngine(global_dim=50)

    def test_local_training(self):
        initial = np.ones(50, dtype=np.float32)
        res = self.engine.simulate_local_training(initial, client_id=1, data_volume=100)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        self.assertEqual(out["weights"].shape, (50,))
        self.assertEqual(out["data_volume"], 100)
        # Weights should have shifted slightly from 1
        self.assertFalse(np.allclose(out["weights"], initial))

    def test_federated_round(self):
        res = self.engine.execute_federated_round(num_clients=5)
        self.assertTrue(res.is_ok)
        out = res.unwrap()
        self.assertEqual(out["participated"], 5)
        self.assertEqual(out["global_weights"].shape, (50,))


class TestPracticalAiEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniPracticalAiEngine()
        self.train_docs = [
            "the quick brown fox",
            "jumps over the lazy dog",
            "quick rabbit runs away",
            "brown bear sleeps"
        ]
        self.train_labels = np.array([1, 0, 1, 0]) # e.g., predicting things that are fast

    def test_tfidf_vectorizer(self):
        res = self.engine.fit_transform_tfidf(self.train_docs)
        self.assertTrue(res.is_ok)
        matrix = res.unwrap()
        self.assertEqual(matrix.shape[0], 4)
        self.assertGreater(matrix.shape[1], 5) # depends on unique words (~11)
        
        # Test transform on new text
        res2 = self.engine.transform_tfidf(["fast brown fox"])
        self.assertTrue(res2.is_ok)
        m2 = res2.unwrap()
        self.assertEqual(m2.shape, (1, matrix.shape[1]))

    def test_logistic_regression(self):
        # 1. Fit TF-IDF
        matrix = self.engine.fit_transform_tfidf(self.train_docs).unwrap()
        
        # 2. Train classifier
        res_fit = self.engine.fit_logistic_regression(matrix, self.train_labels, epochs=100, lr=0.5)
        self.assertTrue(res_fit.is_ok)
        
        # 3. Predict on training data (should overfit easily on 4 samples)
        res_pred = self.engine.predict_logistic_regression(matrix)
        self.assertTrue(res_pred.is_ok)
        preds = res_pred.unwrap()["classes"]
        
        # Let's just check the shapes match
        self.assertEqual(preds.shape, (4,))


if __name__ == '__main__':
    unittest.main()
