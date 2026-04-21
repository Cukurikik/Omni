import unittest
import numpy as np

# Batches
from omni_spark_mllib_analysis_engine import OmniSparkMLLibAnalysisEngine, Ok as SparkOk, Err as SparkErr
from omni_physo_symbolic_engine import OmniPhysoSymbolicEngine, Ok as PhysoOk, Err as PhysoErr
from omni_fissure_rf_security_engine import OmniFissureRFSecurityEngine, Ok as RF_Ok, Err as RF_Err

class TestBatch12HardcodedEngines(unittest.TestCase):
    def test_spark_als(self):
        engine = OmniSparkMLLibAnalysisEngine()
        user_factor = np.random.randn(10, 4)
        interaction_matrix = np.random.randn(10, 5)
        res = engine.execute_als_linear_factorization_step(user_factor, interaction_matrix)
        self.assertIsInstance(res, SparkOk)
        self.assertEqual(res.value["solved_item_features_matrix"].shape, (5, 4))
        
    def test_physo(self):
        engine = OmniPhysoSymbolicEngine()
        # Mock physics: y = x^2
        def physics_law(x): return x ** 2
        x_val = np.array([1, 2, 3, 4])
        y_val = np.array([1, 4, 9, 16])
        res = engine.validate_symbolic_expression(x_val, y_val, physics_law)
        self.assertIsInstance(res, PhysoOk)
        self.assertTrue(res.value["is_physically_sound"])
        self.assertEqual(res.value["scientific_rmse"], 0.0)

    def test_rf_security(self):
        engine = OmniFissureRFSecurityEngine(spike_threshold=0.5)
        # Bikin sinyal complex biasa
        time = np.linspace(0, 1, 100)
        signal = np.sin(2 * np.pi * 5 * time) + 1j * np.cos(2 * np.pi * 5 * time)
        # Menambahkan Anomaly murni secara riil
        signal[10:15] += 10.0 
        
        res = engine.process_radio_iq_signal(signal)
        self.assertIsInstance(res, RF_Ok)
        
if __name__ == "__main__":
    unittest.main()
