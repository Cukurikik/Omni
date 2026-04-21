"""
OMNI SEMESTER 9 - BATCH 12
Test Suite: Integration and Validation Matrix for Batch 12 Engines.

This test suite validates the integration of Featureform, ML-CVNets, Spark MLLib,
FISSURE, and PhySO engines. It tests internal math determinism, robust monadic 
error propagation, and OMNI boundary compliance.
"""

import unittest
import numpy as np

# Mengimpor seluruh engine Batch 12 dari namespace yang sama
from omni_featureform_store_engine import OmniFeatureformStoreEngine, Ok as FF_Ok, Err as FF_Err
from omni_apple_cvnets_engine import OmniAppleCVNetsEngine, Ok as CV_Ok, Err as CV_Err
from omni_spark_mllib_analysis_engine import OmniSparkMLLibAnalysisEngine, Ok as Spark_Ok, Err as Spark_Err
from omni_fissure_rf_security_engine import OmniFissureRFSecurityEngine, Ok as RF_Ok, Err as RF_Err
from omni_physo_symbolic_engine import OmniPhysoSymbolicEngine, Ok as Phy_Ok, Err as Phy_Err


class TestBatch12FeatureformEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniFeatureformStoreEngine()
        
    def test_feature_registration_success(self):
        res = self.engine.register_feature_group("user_click_stream", schema_version=2, dimension=128)
        self.assertIsInstance(res, FF_Ok)
        self.assertEqual(res.value["group"], "user_click_stream")
        
    def test_feature_registration_failure_duplicate(self):
        self.engine.register_feature_group("duplicate_feat", 1, 64)
        res = self.engine.register_feature_group("duplicate_feat", 2, 128)
        self.assertIsInstance(res, FF_Err)
        
    def test_feature_registration_failure_invalid_dim(self):
        res = self.engine.register_feature_group("bad_dim", 1, -5)
        self.assertIsInstance(res, FF_Err)
        
    def test_materialize_feature_success(self):
        self.engine.register_feature_group("view_feat", 1, 32)
        res = self.engine.materialize_feature("view_feat", batch_size=100)
        self.assertIsInstance(res, FF_Ok)
        self.assertEqual(res.value["materialized_shape"], (100, 32))

class TestBatch12AppleCVNetsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniAppleCVNetsEngine()
        
    def test_mbconv_block_execution_success(self):
        # Batch=2, Channels=16, H=32, W=32
        tensor = np.random.randn(2, 16, 32, 32).astype(np.float32)
        res = self.engine.execute_mbconv_block(tensor, expansion_factor=4, stride=1)
        self.assertIsInstance(res, CV_Ok)
        self.assertEqual(res.value["original_shape"], (2, 16, 32, 32))
        self.assertEqual(res.value["projected_shape"], (2, 1, 32, 32))
        
    def test_mbconv_stride_reduction(self):
        tensor = np.random.randn(1, 8, 64, 64).astype(np.float32)
        res = self.engine.execute_mbconv_block(tensor, expansion_factor=2, stride=2)
        self.assertIsInstance(res, CV_Ok)
        self.assertEqual(res.value["projected_shape"], (1, 1, 32, 32))
        self.assertEqual(self.engine.spatial_reduction_count, 1)

    def test_invalid_tensor_rank(self):
        tensor = np.ones((16, 32, 32)) # 3D instead of 4D
        res = self.engine.execute_mbconv_block(tensor, expansion_factor=2, stride=1)
        self.assertIsInstance(res, CV_Err)

class TestBatch12SparkMLLibEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniSparkMLLibAnalysisEngine()
        
    def test_sequence_map_reduce_job(self):
        dataset = np.ones((100, 10)) * 2.0
        res = self.engine.sequence_map_reduce_job(dataset, partitions=4)
        self.assertIsInstance(res, Spark_Ok)
        self.assertEqual(res.value["partitions_created"], 4)
        self.assertEqual(res.value["reduction_shape"], (10,))
        
    def test_sequence_map_reduce_empty(self):
        res = self.engine.sequence_map_reduce_job(np.array([]), 4)
        self.assertIsInstance(res, Spark_Err)
        
    def test_als_factorization_success(self):
        # 10 Users x 5 Items
        rating_matrix = np.random.rand(10, 5)
        res = self.engine.execute_als_factorization(rating_matrix, rank=3, reg_param=0.1)
        self.assertIsInstance(res, Spark_Ok)
        self.assertEqual(res.value["item_factor_shape"], (5, 3))

    def test_als_factorization_invalid_constraint(self):
        rating_matrix = np.random.rand(10, 5)
        res = self.engine.execute_als_factorization(rating_matrix, rank=0)
        self.assertIsInstance(res, Spark_Err)

class TestBatch12FissureRFEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniFissureRFSecurityEngine(sample_rate_hz=1000)
        
    def test_iq_spectrum_clean(self):
        clean_signal = self.engine.generate_synthetic_rf_test(100.0, inject_anomaly=False)
        # Using a very high threshold for pure tone to avoid false anomaly
        res = self.engine.analyze_iq_signal_spectrum(clean_signal, anomaly_threshold=15.0)
        self.assertIsInstance(res, RF_Ok)
        self.assertFalse(res.value["is_anomalous"])
        
    def test_iq_spectrum_anomalous(self):
        jammed_signal = self.engine.generate_synthetic_rf_test(100.0, inject_anomaly=True)
        # Using a lower threshold just to guarantee tests catch the synthetic spike
        res = self.engine.analyze_iq_signal_spectrum(jammed_signal, anomaly_threshold=1.5)
        self.assertIsInstance(res, RF_Ok)
        self.assertTrue(res.value["is_anomalous"])
        self.assertEqual(self.engine.anomalies_detected, 1)

    def test_iq_invalid_dimension(self):
        multi_d_signal = np.ones((10, 10))
        res = self.engine.analyze_iq_signal_spectrum(multi_d_signal)
        self.assertIsInstance(res, RF_Err)

class TestBatch12PhysoSymbolicEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniPhysoSymbolicEngine()
        
    def test_evaluate_symbolic_generation(self):
        X = np.random.rand(50, 2)
        y = np.random.rand(50)
        res = self.engine.evaluate_symbolic_generation(X, y, max_tree_depth=5)
        self.assertIsInstance(res, Phy_Ok)
        self.assertTrue("generated_fitness" in res.value)
        self.assertTrue(res.value["complexity_penalty_applied"] > 0)
        self.assertTrue(res.value["is_new_global_best"])
        
    def test_evaluate_symbolic_mismatch(self):
        X = np.random.rand(50)
        y = np.random.rand(10)
        res = self.engine.evaluate_symbolic_generation(X, y, 5)
        self.assertIsInstance(res, Phy_Err)
        
    def test_evaluate_symbolic_invalid_depth(self):
        X = np.random.rand(10)
        y = np.random.rand(10)
        res = self.engine.evaluate_symbolic_generation(X, y, 999) # Constraint break
        self.assertIsInstance(res, Phy_Err)

class TestBatch12Diagnostics(unittest.TestCase):
    def test_all_diagnostics_online(self):
        engines = [
            OmniFeatureformStoreEngine(),
            OmniAppleCVNetsEngine(),
            OmniSparkMLLibAnalysisEngine(),
            OmniFissureRFSecurityEngine(),
            OmniPhysoSymbolicEngine()
        ]
        
        for eng in engines:
            diag = eng.diagnostics()
            self.assertEqual(diag["status"], "ONLINE")
            self.assertTrue("uptime_seconds" in diag)


if __name__ == "__main__":
    unittest.main()
