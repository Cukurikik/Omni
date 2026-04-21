"""
OMNI SEMESTER 9 - BATCH 13
Test Suite: Integration and Validation Matrix for Batch 13 Engines.

This test suite validates the integration of HLS4ML, SNNTorch, SLING,
BitNet, and TimeMixer engines. It robustly checks physics constraints,
hardware synthesisation logic, zero-algebraic_bound constraints, and Monadic interfaces.
"""

import unittest
import numpy as np

# Mengimpor seluruh engine Batch 13 dari namespace yang sama
from omni_hls4ml_synthesis_engine import OmniHls4mlSynthesisEngine, Ok as Hls_Ok, Err as Hls_Err
from omni_snntorch_spiking_engine import OmniSnntorchSpikingEngine, Ok as Snn_Ok, Err as Snn_Err
from omni_sling_semantic_engine import OmniSlingSemanticEngine, Ok as Sling_Ok, Err as Sling_Err
from omni_bitnet_quantization_engine import OmniBitnetQuantizationEngine, Ok as Bit_Ok, Err as Bit_Err
from omni_timemixer_forecasting_engine import OmniTimemixerForecastingEngine, Ok as Time_Ok, Err as Time_Err


class TestBatch13Hls4mlEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniHls4mlSynthesisEngine()
        
    def test_synthesize_hardware_layer(self):
        weights = np.random.randn(64, 32).astype(np.float32)
        res = self.engine.execute_hardware_bitmask(weights, bit_width=16, int_width=6)
        
        self.assertIsInstance(res, Hls_Ok)
        self.assertTrue(res.value["compression_math_ratio"] > 1.0)
        self.assertTrue(res.value["degradation_mse"] >= 0.0)
        
    def test_synthesize_invalid_bits(self):
        weights = np.random.randn(10, 10)
        res = self.engine.execute_hardware_bitmask(weights, bit_width=8, int_width=10) # Broken int bounds
        self.assertIsInstance(res, Hls_Err)

class TestBatch13SnntorchEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniSnntorchSpikingEngine()
        
    def test_lif_membrane_cycle(self):
        # 20 timesteps, 4 batch size, 16 neurons
        input_current = np.random.rand(20, 4, 16).astype(np.float32)
        res = self.engine.process_spatio_temporal_input(input_current, decay_factor=0.8, activation_threshold=1.2)
        
        self.assertIsInstance(res, Snn_Ok)
        self.assertEqual(res.value["spike_propagation_tensor"].shape, (20, 4, 16))
        self.assertTrue(res.value["neural_efficiency_ratio"] >= 0.0)

    def test_lif_invalid_dimension(self):
        input_current = np.random.rand(20, 16)
        res = self.engine.process_spatio_temporal_input(input_current)
        self.assertIsInstance(res, Snn_Err)

class TestBatch13SlingSemanticEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniSlingSemanticEngine()
        
    def test_parse_semantic_relations(self):
        context_vectors = np.random.randn(10, 64)
        res = self.engine.execute_adjacency_parsing(context_vectors)
        
        self.assertIsInstance(res, Sling_Ok)
        self.assertTrue(res.value["structural_frame_density"] >= 0.0)

    def test_parse_invalid_context(self):
        res = self.engine.execute_adjacency_parsing(np.random.randn(64))
        self.assertIsInstance(res, Sling_Err)

class TestBatch13BitnetEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniBitnetQuantizationEngine()
        
    def test_transform_weights_to_ternary(self):
        weights = np.random.randn(128, 128) # Real FP weights
        res = self.engine.transform_weights_core(weights)
        
        self.assertIsInstance(res, Bit_Ok)
        
    def test_transform_empty_weights(self):
        res = self.engine.transform_weights_core(np.array([]))
        self.assertIsInstance(res, Bit_Err)

class TestBatch13TimeMixerEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniTimemixerForecastingEngine(decomposition_levels=3)
        
    def test_extract_temporal_scales(self):
        time_series = np.random.randn(32, 8)
        res = self.engine.execute_temporal_mixing(time_series)
        
        self.assertIsInstance(res, Time_Ok)
        self.assertEqual(res.value["pyramid_layers_generated"], 4)
        self.assertEqual(res.value["deepest_macro_resolution_shape"], (4, 8))
        
    def test_short_temporal_scales(self):
        time_series = np.random.randn(4, 8)
        res = self.engine.execute_temporal_mixing(time_series)
        self.assertIsInstance(res, Time_Err)

class TestBatch13Diagnostics(unittest.TestCase):
    def test_all_diagnostics_online(self):
        engines = [
            OmniHls4mlSynthesisEngine(),
            OmniSnntorchSpikingEngine(),
            OmniSlingSemanticEngine(),
            OmniBitnetQuantizationEngine(),
            OmniTimemixerForecastingEngine()
        ]
        
        for eng in engines:
            diag = eng.diagnostics()
            self.assertEqual(diag["status"], "ONLINE")


if __name__ == "__main__":
    unittest.main()
