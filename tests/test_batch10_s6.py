import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core')))

from omni_chainer_engine import OmniChainerEngine, Variable
from omni_tf_deep_learning_engine import OmniTfDeepLearningEngine, NativeDenseLayer
from omni_chinese_clip_engine import OmniChineseClipEngine
from omni_x_transformers_engine import OmniXTransformersEngine, TransformerConfig
from omni_gorgonia_engine import OmniGorgoniaEngine, Node

class TestChainerEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniChainerEngine()

    def test_dynamic_graph_tracing(self):
        v1 = Variable(np.array([2.0]))
        v2 = Variable(np.array([3.0]))
        
        # y = (v1 * v2) + v1 -> 2*3 + 2 = 8
        out1_res = self.engine.dynamic_mul(v1, v2)
        out1 = out1_res.unwrap()
        
        final_res = self.engine.dynamic_add(out1, v1)
        y = final_res.unwrap()
        
        self.assertEqual(y.data[0], 8.0)
        
        # Trace backwards executing topological propagation limits natively
        self.engine.execute_graph_propagation([v1, v2], y)
        
        # dy/dv2 = v1 = 2
        # dy/dv1 = v2 + 1 = 4
        self.assertEqual(v2.grad[0], 2.0)
        self.assertEqual(v1.grad[0], 4.0)

class TestTfDeepLearningEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniTfDeepLearningEngine()

    def test_sequential_dense_bounds(self):
        self.engine.add(NativeDenseLayer(units=16, activation='relu'))
        self.engine.add(NativeDenseLayer(units=3, activation='softmax'))
        
        # Input shape 10
        comp_res = self.engine.compile_model(input_shape=10)
        self.assertTrue(comp_res.is_ok)
        
        x = np.random.randn(5, 10).astype(np.float32) # Batch 5
        pred_res = self.engine.predict(x)
        self.assertTrue(pred_res.is_ok)
        
        preds = pred_res.unwrap()["predictions"]
        
        self.assertEqual(preds.shape, (5, 3))
        # Validate softmax boundaries (probabilities sum to 1)
        np.testing.assert_allclose(np.sum(preds, axis=-1), np.ones(5), rtol=1e-5)

class TestChineseClipEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniChineseClipEngine()

    def test_contrastive_logits(self):
        # D=128
        img_emb = np.random.randn(4, 128)
        txt_emb = np.random.randn(4, 128)
        
        res = self.engine.compute_joint_similarity_logits(img_emb, txt_emb)
        self.assertTrue(res.is_ok)
        
        val = res.unwrap()
        
        logits_i = val["logits_per_image"]
        probs_t = val["probs_per_text"]
        
        self.assertEqual(logits_i.shape, (4, 4))
        self.assertEqual(probs_t.shape, (4, 4))
        
        # Probs per text should sum to 1 along the image axis
        np.testing.assert_allclose(np.sum(probs_t, axis=-1), np.ones(4), rtol=1e-5)

class TestXTransformersEngine(unittest.TestCase):
    def setUp(self):
        self.config = TransformerConfig(d_model=64, n_heads=4, n_layers=2, d_ff=128, vocab_size=1000, max_seq_len=32)
        self.engine = OmniXTransformersEngine(self.config)

    def test_attention_rope_boundaries(self):
        # Test that forward pass produces correct logit shapes with RoPE enabled
        token_ids = np.random.randint(0, 1000, (2, 10))
        logits = self.engine.forward(token_ids)
        
        # Logits shape: (batch=2, seq=10, vocab=1000)
        self.assertEqual(logits.shape, (2, 10, 1000))
        
        # Verify autoregressive generation works
        generated = self.engine.generate(token_ids, max_new_tokens=5, greedy=True)
        self.assertEqual(generated.shape, (2, 15))  # 10 prompt + 5 generated

class TestGorgoniaEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniGorgoniaEngine()

    def test_ast_symbolic_evaluation(self):
        # Symbolic Graph Definition:  c = a * b + 5.0
        v_a = self.engine.create_variable("a").unwrap()
        v_b = self.engine.create_variable("b").unwrap()
        c_5 = self.engine.create_constant("five", np.array([5.0])).unwrap()
        
        mul_node = self.engine.mul(v_a, v_b).unwrap()
        out_node = self.engine.add(mul_node, c_5).unwrap()
        
        # Evaluator Feed Dictionary State Mapping
        state = {
            "a": np.array([2.0]),
            "b": np.array([10.0])
        }
        
        # 2*10 + 5 = 25
        res = self.engine.execute_graph(out_node, feed_dict=state)
        self.assertTrue(res.is_ok)
        
        val = res.unwrap()["evaluation"]
        self.assertEqual(val[0], 25.0)

if __name__ == '__main__':
    unittest.main()
