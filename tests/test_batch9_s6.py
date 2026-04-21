import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core')))

from omni_hyperlpr_engine import OmniHyperLprEngine
from omni_ai_deadlines_engine import OmniAiDeadlinesEngine
from omni_swift_ai_engine import OmniSwiftAiEngine
from omni_gluon_cv_engine import OmniGluonCvEngine
from omni_math_for_ml_engine import OmniMathForMlEngine

class TestHyperLprEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniHyperLprEngine(plate_aspect_ratio_range=(1.0, 10.0))

    def test_density_bounding(self):
        # Create a synthetic image bounding box (e.g., license plate)
        image = np.zeros((100, 200), dtype=np.float32)
        # Create an artificial high-frequency/edge region simulating plate characters
        image[40:60, 50:150] = np.random.rand(20, 100) * 0.8 + 0.2
        
        res = self.engine.detect_plate_bounds(image)
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        self.assertTrue(val["detected"])
        self.assertIsNotNone(val["bbox"])
        self.assertTrue(val["peak_density"] > 0)

class TestAiDeadlinesEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniAiDeadlinesEngine()

    def test_time_decay_metrics(self):
        current_t = 1000.0
        # passed, close, far
        deadlines = np.array([900.0, 1005.0, 2000.0]) 
        res = self.engine.compute_decay_matrix(current_t, deadlines)
        
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        urgency = val["urgency_matrix"]
        states = val["states"]
        
        self.assertEqual(urgency[0], 1.0) # Passed
        self.assertTrue(urgency[1] > urgency[2]) # Closer deadline should have higher urgency than far
        self.assertEqual(states[0], "EXPIRED/REACHED")

class TestSwiftAiEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniSwiftAiEngine(layer_sizes=[10, 5, 2])

    def test_dense_propagation(self):
        input_vec = np.random.randn(4, 10).astype(np.float32) # batch size 4
        res = self.engine.fast_forward_pass(input_vec)
        
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        preds = val["predictions"]
        
        self.assertEqual(preds.shape, (4, 2))
        
        # Softmax validation (sums to ~1.0)
        sums = np.sum(preds, axis=1)
        np.testing.assert_allclose(sums, np.ones(4), rtol=1e-5)

class TestGluonCvEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniGluonCvEngine(in_channels=3, out_channels=4, kernel_size=3)

    def test_convolution_and_pooling(self):
        # B=2, C=3, H=16, W=16
        img = np.random.randn(2, 3, 16, 16).astype(np.float32)
        
        conv_res = self.engine.compute_spatial_convolution(img, stride=1, padding=1)
        self.assertTrue(conv_res.is_ok)
        features = conv_res.unwrap()["feature_maps_extracted"]
        self.assertEqual(features.shape, (2, 4, 16, 16)) # Output sizes should match with pad=1/stride=1
        
        pool_res = self.engine.compute_max_pooling(features, pool_size=2, stride=2)
        self.assertTrue(pool_res.is_ok)
        pooled = pool_res.unwrap()["pooled_maps"]
        self.assertEqual(pooled.shape, (2, 4, 8, 8)) # Halved spatial dimensions

class TestMathForMlEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniMathForMlEngine(n_components=2)

    def test_explicit_pca(self):
        # N=10, D=5
        X = np.random.randn(10, 5)
        # Induce high correlation in first two columns
        X[:, 1] = X[:, 0] * 2.5 + np.random.randn(10) * 0.1
        
        res = self.engine.fast_principal_component_analysis(X)
        self.assertTrue(res.is_ok)
        val = res.unwrap()
        
        proj = val["projected_data"]
        axes = val["principal_axes"]
        var_ratios = val["explained_variances_ratios"]
        
        self.assertEqual(proj.shape, (10, 2))
        self.assertEqual(axes.shape, (5, 2))
        # First component should explain highly significant variance
        self.assertTrue(var_ratios[0] > 0.4)

if __name__ == '__main__':
    unittest.main()
