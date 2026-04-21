import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core')))

from omni_recommender_engine import OmniRecommenderEngine
from omni_wav2letter_engine import OmniWav2LetterEngine
from omni_ml_foundations_engine import OmniMlFoundationsEngine
from omni_kaggle_solutions_engine import OmniKaggleSolutionsEngine
from omni_boss_sensor_engine import OmniBossSensorEngine

class TestRecommenderEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniRecommenderEngine(num_users=10, num_items=10, latent_dim=4)

    def test_mf_sgd(self):
        self.engine.feed_interaction(1, 2, 4.5)
        self.engine.feed_interaction(3, 4, 1.0)
        self.engine.feed_interaction(1, 4, 2.0)
        
        res = self.engine.fit(epochs=5, lr=0.01)
        self.assertTrue(res.is_ok)
        self.assertIn("final_mse", res.unwrap())
        
        pred = self.engine.predict(1, 2)
        self.assertTrue(pred.is_ok)
        self.assertIsInstance(pred.unwrap(), float)

class TestWav2LetterEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniWav2LetterEngine(in_channels=13, out_channels=8, kernel_size=3, vocab_size=5)

    def test_acoustic_forward(self):
        # B=2, C=13, T=10
        seq = np.random.randn(2, 13, 10).astype(np.float32)
        res = self.engine.forward_acoustic_model(seq)
        self.assertTrue(res.is_ok)
        probs = res.unwrap()["probabilities"]
        # T_out = 10 - 3 + 1 = 8
        self.assertEqual(probs.shape, (2, 8, 5))

    def test_greedy_ctc(self):
        probs = np.zeros((1, 5, 5), dtype=np.float32)
        # Sequence: [1, 1, 0(blank), 2, 2] -> decoded should be [1, 2]
        probs[0, 0, 1] = 1.0
        probs[0, 1, 1] = 1.0
        probs[0, 2, 0] = 1.0 
        probs[0, 3, 2] = 1.0
        probs[0, 4, 2] = 1.0
        
        res = self.engine.naive_greedy_ctc_decode(probs, blank_idx=0)
        self.assertTrue(res.is_ok)
        self.assertEqual(res.unwrap()[0], [1, 2])

class TestMlFoundationsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniMlFoundationsEngine(min_samples_split=2, max_depth=3, n_trees=2)

    def test_random_forest(self):
        X = np.array([
            [1, 2], [1, 3], [5, 5], [5, 6]
        ])
        y = np.array([0, 0, 1, 1])
        
        fit_res = self.engine.fit(X, y)
        self.assertTrue(fit_res.is_ok)
        
        pred_res = self.engine.predict(np.array([[1, 2.5], [5, 5.5]]))
        self.assertTrue(pred_res.is_ok)
        self.assertEqual(list(pred_res.unwrap()), [0, 1])

class TestKaggleSolutionsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniKaggleSolutionsEngine(n_estimators=3, learning_rate=0.1, max_depth=2)

    def test_gradient_boosting(self):
        X = np.array([
            [1.0], [2.0], [3.0], [4.0]
        ])
        y = np.array([1.0, 2.0, 3.0, 4.0])
        
        res = self.engine.fit(X, y)
        self.assertTrue(res.is_ok)
        
        pred_res = self.engine.predict(np.array([[2.5]]))
        self.assertTrue(pred_res.is_ok)
        self.assertEqual(pred_res.unwrap().shape, (1,))

class TestBossSensorEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniBossSensorEngine(threshold=0.5)

    def test_sliding_window(self):
        # Create a small image
        img = np.random.randn(16, 16, 3).astype(np.float32)
        res = self.engine.scan_camera_feed(img)
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        self.assertIn("detected", val)
        self.assertIn("bounding_box", val)

if __name__ == '__main__':
    unittest.main()
