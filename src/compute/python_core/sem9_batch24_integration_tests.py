import os
import sys
import unittest
import logging
from typing import Dict, Any

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] OMNI_INTEGRATION_TEST_BATCH24: %(message)s")
logger = logging.getLogger(__name__)

# Dynamically add the compute domain path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from omni_fast_text_multilingual_engine import OmniFastTextMultilingualEngine
from omni_sockeye_engine import OmniSockeyeEngine
from omni_stream_speech_engine import OmniStreamSpeechEngine
from omni_nlg_eval_engine import OmniNlgEvalEngine
from omni_nematus_engine import OmniNematusEngine

class TestOmniBatch24Integration(unittest.TestCase):
    """
    Integration Tests for OMNI Semester 9 Batch 24 Engines.
    Validates structural abstractions bounding Multilingual, MXNet, Wait-K Speech, Metric Evaluation, and Theano bounds dynamically.
    """

    @classmethod
    def setUpClass(cls):
        logger.info("Initializing Batch 24 Engines for Integration Testing")
        cls.fasttext = OmniFastTextMultilingualEngine()
        cls.sockeye = OmniSockeyeEngine()
        cls.stream = OmniStreamSpeechEngine()
        cls.nlg = OmniNlgEvalEngine()
        cls.nematus = OmniNematusEngine()

    def test_fasttext_multilingual_bounds(self):
        logger.info("Testing OmniFastTextMultilingualEngine...")
        # src: 10000, tgt: 15000, dim: 300
        res = self.fasttext.compute_alignment_matrix_bound(10000, 15000, 300)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["source_embedding_bytes"], 10000 * 300 * 4) # 12000000
        self.assertEqual(res["target_embedding_bytes"], 15000 * 300 * 4) # 18000000
        self.assertTrue(res["total_alignment_memory_limit"] > 0)
        
    def test_sockeye_layer_limit(self):
        logger.info("Testing OmniSockeyeEngine...")
        # batch=32, seq=50, L=6, h=512.
        # act: 32 * 50 * 512 * 4 = 3276800.
        # tot: 3276800 * 6 * 2 = 39321600.
        res = self.sockeye.evaluate_sockeye_layer_bounds(32, 50, 6, 512)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["activation_bound_bytes"], 39321600)
        self.assertTrue(res["mxnet_gradient_map_bytes"] > 0)
        
    def test_stream_speech_map(self):
        logger.info("Testing OmniStreamSpeechEngine...")
        # src: 100, k: 5, latency: 15.5
        # wait: 5 (since 5 < 100)
        # comp: 15.5 * 100 = 1550
        # AL: (5 * 20.0) + (1550 / 100) = 100 + 15.5 = 115.5
        res = self.stream.calculate_wait_k_temporal_limits(100, 5, 15.5) 
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["wait_delay_units"], 5)
        self.assertEqual(res["total_inference_delay_ms"], 1550)
        self.assertEqual(res["theoretical_average_lag_ms"], 115.5)
        
    def test_nlg_eval_vars(self):
        logger.info("Testing OmniNlgEvalEngine...")
        # hyp: 100, avg: 20, n: 4
        # ngram: 100 * 20 * 4 = 8000
        # metric: 8000 * 8 = 64000
        # dense: 100 * 512 * 4 = 204800
        # total: 64000 + 204800 = 268800
        res = self.nlg.compute_evaluation_metric_complexity(100, 20, 4)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["ngram_extraction_count"], 8000)
        self.assertEqual(res["total_evaluation_memory_bytes"], 268800)
        
    def test_nematus_theano_geom(self):
        logger.info("Testing OmniNematusEngine...")
        # batch: 64, seq_len: 30, state: 1024
        # mem: 64 * 30 * 1024 * 4 = 7864320
        # theano: 7864320 * 3 = 23592960
        # total: 7864320 + 23592960 = 31457280
        res = self.nematus.calculate_theano_graph_mapping(64, 30, 1024)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["hidden_state_memory_bytes"], 7864320)
        self.assertEqual(res["compiled_graph_byte_limit"], 31457280)

if __name__ == '__main__':
    print(f"OMNI BATCH 24 SEMESTER 9 - INTEGRATION TESTS STARTING")
    unittest.main(verbosity=2)
