"""
OMNI Framework - Semester 6 Batch 14 Integration Tests
======================================================
Validates all execution structures mapped in:
1. start_ml_engine (KMeans, PCA, Linear Regression)
2. ssd_engine (IoU, NMS, Prior Boxes)
3. sahi_engine (Slices, Mergers)
4. synapse_ml_engine (Distributed DataFrames, LightGBM abstract, Pipelines)
5. tensorspace_engine (3D Spatial Topological mappings)

Zero-algebraic_bound compliance enforced via `Ok` / `Err` Result assertions.
"""

import sys
import os
import unittest
import numpy as np

# Ensure exact path routing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from compute.python_core.omni_start_ml_engine import OmniStartMLEngine, Ok, Err
from compute.python_core.omni_ssd_engine import OmniSSDEngine
from compute.python_core.omni_sahi_engine import OmniSAHIEngine
from compute.python_core.omni_synapse_ml_engine import OmniSynapseMLEngine, Estimator, Transformer, OmniDataFrame
from compute.python_core.omni_tensorspace_engine import OmniTensorSpaceEngine


class StandardTransformer(Transformer):
    def transform(self, dataset: OmniDataFrame):
        return Ok(dataset.map_partitions(lambda x: x * 2))


class TestBatch14Semester6(unittest.TestCase):

    def setUp(self):
        self.start_ml = OmniStartMLEngine()
        self.ssd = OmniSSDEngine()
        self.sahi = OmniSAHIEngine()
        self.synapse = OmniSynapseMLEngine()
        self.tensorspace = OmniTensorSpaceEngine()

    # ---------------------------------------------------------
    # 1. START ML ENGINE TESTS
    # ---------------------------------------------------------
    def test_start_ml_linear_regression(self):
        lr = self.start_ml.create_linear_regression()
        # y = 2x1 + 3x2 + 4
        X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]], dtype=float)
        y = np.array([9, 12, 14, 17], dtype=float)
        
        res = lr.fit(X, y)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(res.value)
        
        # Test predictions
        X_test = np.array([[3, 5]]) # 2*3 + 3*5 + 4 = 6 + 15 + 4 = 25
        pred_res = lr.predict(X_test)
        self.assertEqual(pred_res.__class__.__name__, "Ok")
        self.assertAlmostEqual(pred_res.value[0], 25.0, places=4)

    def test_start_ml_pca(self):
        pca = self.start_ml.create_pca(n_components=1)
        X = np.array([[1, 2], [2, 4], [3, 6], [4, 8]], dtype=float)
        res = pca.fit_transform(X)
        self.assertEqual(res.__class__.__name__, "Ok")
        projected = res.value
        self.assertEqual(projected.shape, (4, 1))

    # ---------------------------------------------------------
    # 2. SSD ENGINE TESTS
    # ---------------------------------------------------------
    def test_ssd_iou_and_nms(self):
        ops = self.ssd.get_operations()
        
        # Two highly overlapping boxes, one completely separate
        # xmin, ymin, xmax, ymax
        boxes = np.array([
            [10, 10, 20, 20],  # Box 0: area 100
            [11, 11, 21, 21],  # Box 1: high overlap with 0
            [50, 50, 60, 60],  # Box 2: no overlap
        ], dtype=float)
        
        scores = np.array([0.9, 0.8, 0.95], dtype=float)
        
        res_nms = ops.non_max_suppression(boxes, scores, iou_threshold=0.5)
        self.assertEqual(res_nms.__class__.__name__, "Ok")
        keep = res_nms.value
        
        # Box 2 should be kept (highest score), Box 0 kept (next highest, no overlap), Box 1 suppressed
        self.assertEqual(len(keep), 2)
        self.assertIn(2, keep)
        self.assertIn(0, keep)
        self.assertNotIn(1, keep)

    def test_ssd_prior_boxes(self):
        generator = self.ssd.create_prior_box_generator(
            image_size=300, 
            feature_maps=[38], 
            min_sizes=[30], 
            max_sizes=[60], 
            steps=[8]
        )
        res = generator.forward()
        self.assertEqual(res.__class__.__name__, "Ok")
        priors = res.value
        # 38x38 map * 2 anchors per cell = 2888
        self.assertEqual(priors.shape, (2888, 4))
        self.assertTrue(np.all(priors >= 0.0) and np.all(priors <= 1.0))

    # ---------------------------------------------------------
    # 3. SAHI ENGINE TESTS
    # ---------------------------------------------------------
    def test_sahi_splicing(self):
        slicer = self.sahi.create_slicer(slice_height=512, slice_width=512, overlap_h=0.2, overlap_w=0.2)
        res = slicer.calculate_slices(1000, 1000)
        self.assertEqual(res.__class__.__name__, "Ok")
        slices = res.value
        
        # step = 512 * 0.8 = 409
        # x starts: 0, 409, 1000-512=488. (3 steps for width)
        # y starts: 0, 409, 488. (3 steps for height)
        # Total slices = 9
        self.assertEqual(len(slices), 9)
        self.assertEqual(slices[0].xmin, 0)
        
    def test_sahi_combiner(self):
        comb = self.sahi.get_combiner()
        # box in slice coorids (xmin, ymin, xmax, ymax)
        slice_boxes = np.array([[10, 10, 50, 50]]) 
        res = comb.project_to_parent(slice_boxes, shift_xy=(409, 200))
        self.assertEqual(res.__class__.__name__, "Ok")
        mapped = res.value
        self.assertTrue(np.array_equal(mapped[0], [419, 210, 459, 250]))

    # ---------------------------------------------------------
    # 4. SYNAPSE ML ENGINE TESTS
    # ---------------------------------------------------------
    def test_synapse_pipeline(self):
        # 4 samples, 3 features (last is target)
        data = np.array([
            [1.0, 2.0, 1.0],
            [2.0, 1.0, 0.0],
            [3.0, 3.0, 1.0],
            [0.5, 0.5, 0.0]
        ])
        df = self.synapse.create_dataframe(data, partitions=2)
        
        estimator = self.synapse.create_lightgbm_classifier()
        pipeline = self.synapse.create_pipeline([StandardTransformer(), estimator])
        
        fit_res = pipeline.fit(df)
        self.assertEqual(fit_res.__class__.__name__, "Ok", fit_res.error if fit_res.__class__.__name__ == "Err" else "")
        
        model = fit_res.value
        trans_res = model.transform(df)
        self.assertEqual(trans_res.__class__.__name__, "Ok", trans_res.error if trans_res.__class__.__name__ == "Err" else "")
        
        out_df = trans_res.value
        out_data = out_df.collect()
        # Features modified by StandardTransformer (x2), then augmented with prediction prob target column
        self.assertEqual(out_data.shape[1], 4)

    # ---------------------------------------------------------
    # 5. TENSORSPACE ENGINE TESTS
    # ---------------------------------------------------------
    def test_tensorspace_topology(self):
        builder = self.tensorspace.create_topology_builder(spacing=100)
        res1 = builder.add_conv2d(filters=64, size_x=224, size_y=224)
        self.assertEqual(res1.__class__.__name__, "Ok")
        
        res2 = builder.add_pooling(size_x=112, size_y=112, previous_depth=64)
        self.assertEqual(res2.__class__.__name__, "Ok")
        
        res3 = builder.add_dense(1000)
        self.assertEqual(res3.__class__.__name__, "Ok")
        
        final_res = builder.extract_geometry_flow()
        self.assertEqual(final_res.__class__.__name__, "Ok")
        layers = final_res.value
        
        self.assertEqual(len(layers), 3)
        self.assertEqual(layers[0]["type"], "Conv2D")
        self.assertEqual(layers[1]["type"], "Pooling")
        self.assertEqual(layers[2]["type"], "Dense")
        
        # Check Z dimension mapping
        self.assertEqual(layers[0]["z_offset"], 0.0)
        self.assertEqual(layers[1]["z_offset"], -100.0)
        self.assertEqual(layers[2]["z_offset"], -200.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
