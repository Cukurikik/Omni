import unittest
import numpy as np

# Test imports mapped to OMNI Batch 15 Semester 6 Engines
from src.compute.python_core.omni_dl_pytorch_engine import OmniDLPyTorchEngine
from src.compute.python_core.omni_gluonts_engine import OmniGluonTSEngine
from src.compute.python_core.omni_pose_estimation_engine import OmniPoseEstimationEngine, Peak
from src.compute.python_core.omni_augmentor_engine import OmniAugmentorEngine
from src.compute.python_core.omni_sketch_code_engine import OmniSketchCodeEngine


class TestBatch15Semester6(unittest.TestCase):
    
    def setUp(self):
        # Initialize engines
        self.pytorch = OmniDLPyTorchEngine()
        self.gluon = OmniGluonTSEngine()
        self.pose = OmniPoseEstimationEngine()
        self.augmentor = OmniAugmentorEngine()
        self.sketch = OmniSketchCodeEngine()

    def test_pytorch_forward_and_loss(self):
        """Test fundamental deep learning abstraction mapping"""
        lin = self.pytorch.get_linear_module(in_dim=3, out_dim=2)
        x = self.pytorch.create_tensor([1.0, -1.0, 0.5])
        
        # Forward pass
        res_forward = lin.forward(x)
        self.assertEqual(res_forward.__class__.__name__, "Ok")
        out_tensor = res_forward.value
        self.assertEqual(out_tensor.shape, (1, 2))
        
        # Loss pass
        target = self.pytorch.create_tensor([0.0, 1.0])
        res_loss = self.pytorch.get_mse_loss().mse_loss(out_tensor, target)
        self.assertEqual(res_loss.__class__.__name__, "Ok")
        
    def test_gluonts_probabilistic_unroll(self):
        """Test Recurrent Time Series Forecasting Mockup"""
        # Linear sequence, prediction should follow trajectory
        ts_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
        
        forecaster = self.gluon.create_autoregressive_forecaster(context_length=3, prediction_length=5)
        
        # Fit logic
        res_fit = forecaster.fit(ts_data)
        self.assertEqual(res_fit.__class__.__name__, "Ok")
        
        # Predict logic (Unrolling horizon)
        res_pred = forecaster.predict(ts_data[-3:])
        self.assertEqual(res_pred.__class__.__name__, "Ok")
        
        forecast = res_pred.value
        self.assertEqual(len(forecast.mean), 5)
        self.assertEqual(len(forecast.p10), 5)
        self.assertEqual(len(forecast.p90), 5)
        # Verify sequence unrolled higher than input trajectory
        self.assertTrue(forecast.mean[0] > 10.0)

    def test_pose_estimation_paf_nms(self):
        """Test Heatmap Peaks and PAF scoring integrals natively"""
        processor = self.pose.create_pose_processor(nms_threshold=0.5)
        
        # algebraic_bound 5x5 Heatmap with a single strong peak at (2, 2)
        heatmap = np.zeros((5, 5))
        heatmap[2, 2] = 0.99
        heatmap[2, 3] = 0.3
        
        res_peaks = processor.extract_peaks_from_heatmap(heatmap)
        self.assertEqual(res_peaks.__class__.__name__, "Ok")
        peaks, next_id = res_peaks.value
        
        self.assertEqual(len(peaks), 1)
        self.assertEqual(peaks[0].x, 2)
        self.assertEqual(peaks[0].y, 2)
        
        # Test line integral along fake PAF Map between two arbitrary peaks
        paf_x = np.ones((10, 10)) * 0.5
        paf_y = np.ones((10, 10)) * 0.0
        
        pa = Peak(x=1, y=1, score=1.0, id=0)
        pb = Peak(x=8, y=1, score=1.0, id=1) # Pure rightward direction
        
        # Expected dot product of Unit_X(1,0) dotted with Field(0.5, 0.0) = 0.5
        res_score = processor.compute_paf_score(paf_x, paf_y, pa, pb, num_inter_points=5)
        self.assertEqual(res_score.__class__.__name__, "Ok")
        self.assertAlmostEqual(res_score.value, 0.5)

    def test_augmentor_geometric_pipeline(self):
        """Test probabilistic image dataset operations via pure logic matrices"""
        pipe = self.augmentor.create_pipeline()
        
        # Force operations constantly to test matrices structure
        pipe.add_rotate_90(probability=1.0)
        pipe.add_flip_left_right(probability=1.0)
        
        # algebraic_bound RGB Image 100x200x3
        img = np.zeros((100, 200, 3))
        
        res = pipe.process_image(img)
        self.assertEqual(res.__class__.__name__, "Ok")
        
        # 100x200 rotated 90 deg -> 200x100.
        # Flipping does not alter shape.
        final_img = res.value["image"]
        self.assertEqual(final_img.shape, (200, 100, 3))
        self.assertIn("Rotate90", res.value["applied_operations"])

    def test_sketch_code_compiler(self):
        """Test string/DSL array tree processing mapping tokens to code."""
        compiler = self.sketch.create_compiler()
        
        tokens = [
            "header", "{", 
                "btn-active",
            "}",
            "row", "{",
                "text",
            "}"
        ]
        
        res = compiler.compile(tokens)
        self.assertEqual(res.__class__.__name__, "Ok")
        html_out = res.value
        
        self.assertIn("<div class=\"header\">", html_out)
        self.assertIn("<button class=\"btn btn-primary\">Button</button>", html_out)
        self.assertIn("<p>Loreum ipsum</p>", html_out)

if __name__ == '__main__':
    unittest.main()
