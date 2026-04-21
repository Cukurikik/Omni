"""
OMNI Framework - Semester 6 Batch 13 Integration Test Suite
=============================================================
Validates the structural and functional integrity of the Batch 13 AI Engines:
1. OmniSeq2SeqEngine
2. OmniFlashlightEngine
3. OmniZenMLEngine
4. OmniAIEngineeringEngine
5. OmniGraphNetsEngine
6. OmniDeepLearningEduEngine

Ensures compliance with OMNI Zero-Mock standards and monadic error handling.
"""

import sys
import os
import unittest
import numpy as np

# Adjust path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from compute.python_core.omni_seq2seq_engine import OmniSeq2SeqEngine, Seq2SeqConfig
from compute.python_core.omni_flashlight_engine import OmniFlashlightEngine
from compute.python_core.omni_zenml_engine import OmniZenMLEngine, Pipeline, PipelineStep
from compute.python_core.omni_ai_engineering_engine import OmniAIEngineeringEngine, Document
from compute.python_core.omni_graph_nets_engine import OmniGraphNetsEngine
from compute.python_core.omni_deeplearning_edu_engine import OmniDeepLearningEduEngine

class TestBatch13Semester6(unittest.TestCase):

    def setUp(self):
        self.seq2seq_engine = OmniSeq2SeqEngine(Seq2SeqConfig(max_len=5))
        self.flashlight_engine = OmniFlashlightEngine()
        self.zenml_engine = OmniZenMLEngine()
        self.ai_eng_engine = OmniAIEngineeringEngine()
        self.graph_engine = OmniGraphNetsEngine()
        self.dl_edu_engine = OmniDeepLearningEduEngine()

    # --- 1. Seq2Seq Engine Tests ---
    def test_seq2seq_diagnostics(self):
        diag = self.seq2seq_engine.diagnostics()
        self.assertEqual(diag["engine_id"], "omni-seq2seq")
        self.assertEqual(diag["status"], "operational")

    def test_seq2seq_build_and_forward(self):
        src = [["hello", "world"]]
        tgt = [["hola", "mundo"]]
        self.seq2seq_engine.build_vocabs(src, tgt)
        res = self.seq2seq_engine.translate_greedy(src)
        self.assertIn("translations", res)
        # Verify attention matrix shape (Batch, Out_len, In_len)
        self.assertTrue(len(res["attention"].shape) == 3)

    # --- 2. Flashlight Engine Tests ---
    def test_flashlight_diagnostics(self):
        diag = self.flashlight_engine.diagnostics()
        self.assertEqual(diag["engine_id"], "omni-flashlight")

    def test_flashlight_autograd(self):
        x = self.flashlight_engine.create_variable(np.array([2.0, 3.0]), requires_grad=True)
        y = self.flashlight_engine.create_variable(np.array([4.0, 5.0]), requires_grad=True)
        z = x * y + x
        # Backward simulate scalar
        loss = self.flashlight_engine.create_variable(np.array([1.0, 1.0]))
        z.backward(gradient=loss.data)
        
        self.assertIsNotNone(x.grad)
        self.assertIsNotNone(y.grad)
        # dz/dx = y + 1 => [5.0, 6.0]
        np.testing.assert_array_almost_equal(x.grad, np.array([5.0, 6.0]))

    # --- 3. ZenML Engine Tests ---
    def test_zenml_diagnostics(self):
        diag = self.zenml_engine.diagnostics()
        self.assertEqual(diag["engine_id"], "omni-zenml")

    def test_zenml_pipeline_execution(self):
        @self.zenml_engine.define_step("load_data")
        def load_data():
            return {"data": [1, 2, 3]}

        @self.zenml_engine.define_step("train_model")
        def train_model(data_dict):
            return {"model": "omni_model_v1", "accuracy": 0.99}

        @self.zenml_engine.define_pipeline("training_pipeline")
        def pipe():
            data = load_data()
            model = train_model(data)
            return model

        res = self.zenml_engine.execute(pipe())
        self.assertTrue(hasattr(res, 'value'))
        run = res.value
        self.assertEqual(run.status, "completed")
        self.assertTrue(len(run.artifacts_produced) > 0)

    # --- 4. AI Engineering Engine Tests ---
    def test_ai_engineering_diagnostics(self):
        diag = self.ai_eng_engine.diagnostics()
        self.assertEqual(diag["engine_id"], "omni-ai-engineering")

    def test_ai_engineering_rag(self):
        docs = [
            Document(id="1", content="Omni Framework is built on zero-mock patterns."),
            Document(id="2", content="GCP Deployment requires unified telemetry.")
        ]
        self.ai_eng_engine.add_documents(docs)
        res = self.ai_eng_engine.retrieve("zero mock", top_k=1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0].id, "1")

    # --- 5. Graph Nets Engine Tests ---
    def test_graph_nets_diagnostics(self):
        diag = self.graph_engine.diagnostics()
        self.assertEqual(diag["engine_id"], "omni-graph-nets")

    def test_graph_nets_gcn(self):
        # 3 nodes, 2 edges
        nodes = np.random.randn(3, 4)
        edges = np.random.randn(2, 5)
        senders = np.array([0, 1])
        receivers = np.array([1, 2])
        
        graph = self.graph_engine.create_graph(nodes, edges, senders, receivers)
        gcn = self.graph_engine.create_gcn_layer(in_features=4, out_features=8)
        
        out_graph = gcn(graph)
        self.assertEqual(out_graph.nodes.shape, (3, 8))

    # --- 6. DeepLearning.edu Engine Tests ---
    def test_dledu_diagnostics(self):
        diag = self.dl_edu_engine.diagnostics()
        self.assertEqual(diag["engine_id"], "omni-dl-edu")

    def test_dledu_batch_norm(self):
        bn = self.dl_edu_engine.create_batch_norm(num_features=4)
        x = np.random.randn(10, 4)
        out = bn.forward(x, is_training=True)
        # mean should be ~0, var ~1
        np.testing.assert_array_almost_equal(np.mean(out, axis=0), np.zeros(4), decimal=5)
        np.testing.assert_array_almost_equal(np.var(out, axis=0), np.ones(4), decimal=4)

if __name__ == '__main__':
    unittest.main()
