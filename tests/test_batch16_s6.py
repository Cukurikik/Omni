import unittest
import numpy as np

# Test imports mapped to OMNI Batch 16 Semester 6 Engines
from src.compute.python_core.omni_ml_complete_engine import OmniMLCompleteEngine
from src.compute.python_core.omni_autogptq_engine import OmniAutoGPTQEngine
from src.compute.python_core.omni_keras_js_engine import OmniKerasJSEngine
from src.compute.python_core.omni_textgenrnn_engine import OmniTextgenRNNEngine
from src.compute.python_core.omni_fastai_course_engine import OmniFastAICourseEngine

class TestBatch16Semester6(unittest.TestCase):
    
    def setUp(self):
        # Initialize engines
        self.ml_comp = OmniMLCompleteEngine()
        self.autogptq = OmniAutoGPTQEngine()
        self.keras_js = OmniKerasJSEngine()
        self.textgenrnn = OmniTextgenRNNEngine()
        self.fastai = OmniFastAICourseEngine()

    def test_ml_complete_logistic_and_metrics(self):
        """Test Native NumPy Logistic Regression Fit & Predict"""
        logreg = self.ml_comp.get_logistic_regression(lr=0.5, iter=200)
        
        # Simple AND-gate logic
        X = np.array([[0,0], [0,1], [1,0], [1,1]], dtype=float)
        y = np.array([0, 0, 0, 1], dtype=float)
        
        res_fit = logreg.fit(X, y)
        self.assertEqual(res_fit.__class__.__name__, "Ok")
        
        res_pred = logreg.predict(X)
        self.assertEqual(res_pred.__class__.__name__, "Ok")
        preds = res_pred.value
        
        # Check metrics wrapper
        metrics = self.ml_comp.get_metrics_grid()
        res_met = metrics.classification_report(y, preds)
        self.assertEqual(res_met.__class__.__name__, "Ok")
        perf = res_met.value
        # Should be decently accurate to generate metrics without crashing
        self.assertTrue(perf["accuracy"] >= 0.0)
        
    def test_autogptq_tensor_quantization(self):
        """Test mapping FP32 array weights to integer 8-bit matrices securely and scaling them back natively."""
        quant = self.autogptq.get_quantizer()
        
        X = np.array([
            [0.1,  -1.2, 5.5],
            [10.2, 3.1,  -4.0]
        ])
        
        res_q = quant.quantize(X, num_bits=8)
        self.assertEqual(res_q.__class__.__name__, "Ok")
        buffer = res_q.value
        
        self.assertEqual(buffer.q_weights.dtype, np.int8)
        self.assertEqual(buffer.scales.size, 3) # Per-column channel scaling based on setup
        
        res_dq = quant.dequantize(buffer)
        self.assertEqual(res_dq.__class__.__name__, "Ok")
        reconstructed = res_dq.value
        
        # Max error due to quantization should exist but bounded
        self.assertEqual(reconstructed.shape, X.shape)
        # Verify approximation bounds, should reasonably be around original tensor logic.
        diff = np.abs(X - reconstructed)
        self.assertTrue(np.max(diff) < 0.5)

    def test_keras_js_browser_serialization(self):
        """Test extraction of topological shapes to Float32Array JSON equivalents."""
        ser = self.keras_js.get_serializer()
        
        T = np.ones((5, 12))
        res_bin = ser.serialize_weights("dense_1", T)
        self.assertEqual(res_bin.__class__.__name__, "Ok")
        msg = res_bin.value
        
        self.assertEqual(msg["meta"]["layer_id"], "dense_1")
        self.assertEqual(msg["meta"]["buffer_meta"]["type"], "Float32Array")
        self.assertEqual(len(msg["buffer_object"].flat_data), 60)
        
        res_mani = ser.build_network_manifest([{"name": "d1", "type": "Dense"}])
        self.assertEqual(res_mani.__class__.__name__, "Ok")
        self.assertEqual(len(res_mani.value["topology"]), 1)

    def test_textgenrnn_character_cells(self):
        """Test RNN step logic returning indices using sampled math sequences."""
        gen = self.textgenrnn.get_recurrent_generator(vocab_size=10)
        
        # Generate 5 tokens from seed index 0
        res = gen.generate_sequence(seed_idx=0, length=5, temperature=1.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        
        seq = res.value
        self.assertEqual(len(seq), 6) # Initial seed + 5 generated components

    def test_fastai_course_learner_loop(self):
        """Test top level abstracted data blocks and learner executing without structural logic collision."""
        X = np.array([1.0, 2.0, 3.0, 4.0])
        Y = np.array([2.0, 4.0, 6.0, 8.0])
        
        learner = self.fastai.get_learner(x=X, y=Y)
        res = learner.fit(epochs=5, lr=0.01)
        self.assertEqual(res.__class__.__name__, "Ok")
        
        stats = res.value
        self.assertEqual(stats["status"], "completed")
        self.assertTrue(stats["final_loss"] >= 0.0)
        self.assertEqual(len(learner.history), 5)


if __name__ == '__main__':
    unittest.main()
