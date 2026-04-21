import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core')))

from omni_metric_learning_engine import OmniMetricLearningEngine
from omni_smile_ml_engine import OmniSmileMlEngine
from omni_styletts_engine import OmniStyleTtsEngine
from omni_xlnet_engine import OmniXlnetEngine
from omni_nanodet_engine import OmniNanodetEngine

class TestMetricLearningEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniMetricLearningEngine(margin=1.0)

    def test_triplet_loss(self):
        B, D = 4, 16
        anchor = np.random.randn(B, D).astype(np.float32)
        positive = anchor + np.random.randn(B, D).astype(np.float32) * 0.1
        negative = anchor + np.random.randn(B, D).astype(np.float32) * 2.0
        
        res = self.engine.compute_triplet_loss_and_gradients(anchor, positive, negative)
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        self.assertIn("loss", val)
        self.assertIn("grad_anchor", val)
        self.assertEqual(val["grad_anchor"].shape, (B, D))

class TestSmileMlEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniSmileMlEngine(C=1.0, max_passes=2, kernel_type='linear')

    def test_smo_svm(self):
        # Linearly separable XOR-like (actually let's just make it simple linearly separable)
        X = np.array([
            [1.0, 1.0],
            [2.0, 2.0],
            [-1.0, -1.0],
            [-2.0, -2.0]
        ])
        y = np.array([1, 1, -1, -1])
        
        fit_res = self.engine.fit(X, y)
        self.assertTrue(fit_res.is_ok)
        
        pred_res = self.engine.predict(np.array([[3.0, 3.0], [-3.0, -3.0]]))
        self.assertTrue(pred_res.is_ok)
        self.assertEqual(list(pred_res.unwrap()), [1, -1])

class TestStyleTtsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniStyleTtsEngine(style_dim=128, diffusion_steps=5)

    def test_prosody_diffusion(self):
        text_cond = np.random.randn(2, 128).astype(np.float32)
        res = self.engine.sample_style_acoustic_features(text_cond)
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        self.assertEqual(val["style_vector"].shape, (2, 128))
        self.assertEqual(val["diffusion_steps_completed"], 5)

class TestXlnetEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniXlnetEngine(d_model=64, n_heads=2)

    def test_two_stream_attention(self):
        content = np.random.randn(10, 64).astype(np.float32)
        query = np.random.randn(10, 64).astype(np.float32)
        
        res = self.engine.forward_two_stream_attention(content, query)
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        self.assertEqual(val["content_output"].shape, (10, 64))
        self.assertEqual(val["query_output"].shape, (10, 64))
        self.assertEqual(val["plm_mask"].shape, (10, 10))

class TestNanodetEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniNanodetEngine()

    def test_anchor_free_giou(self):
        centers = np.array([
            [10.0, 10.0],
            [50.0, 50.0]
        ])
        predicted_distances = np.array([
            [5.0, 5.0, 5.0, 5.0],    # produces (5, 5, 15, 15)
            [10.0, 10.0, 10.0, 10.0] # produces (40, 40, 60, 60)
        ])
        gt_boxes = np.array([
            [5.0, 5.0, 15.0, 15.0],
            [41.0, 41.0, 61.0, 61.0] # slight offset
        ])
        
        res = self.engine.compute_regression_loss(centers, predicted_distances, gt_boxes)
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        self.assertTrue(val["mean_giou_loss"] >= 0.0)
        self.assertEqual(val["predicted_boxes"].shape, (2, 4))
        
if __name__ == '__main__':
    unittest.main()
