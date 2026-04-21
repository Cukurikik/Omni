import os
import sys
import unittest
import logging
from typing import Dict, Any

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] OMNI_INTEGRATION_TEST_BATCH19: %(message)s")
logger = logging.getLogger(__name__)

# Dynamically add the compute domain path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from omni_nlp_progress_engine import OmniNlpProgressEngine
from omni_tensor_2_tensor_engine import OmniTensor2TensorEngine
from omni_nemo_engine import OmniNemoEngine
from omni_manga_image_translator_engine import OmniMangaImageTranslatorEngine
from omni_espnet_engine import OmniEspnetEngine

class TestOmniBatch19Integration(unittest.TestCase):
    """
    Integration Tests for OMNI Semester 9 Batch 19 Engines.
    Tests spatial bounding, SOTA bounds logic, and exact macro topologies without loading deep models.
    """

    @classmethod
    def setUpClass(cls):
        logger.info("Initializing Batch 19 Engines for Integration Testing")
        cls.nlp = OmniNlpProgressEngine()
        cls.t2t = OmniTensor2TensorEngine()
        cls.nemo = OmniNemoEngine()
        cls.manga = OmniMangaImageTranslatorEngine()
        cls.espnet = OmniEspnetEngine()

    def test_nlp_progress_tracker(self):
        logger.info("Testing OmniNlpProgressEngine...")
        # Perplexity should be >= 1.0 (Valid)
        res = self.nlp.evaluate_metric_bounds("PERPLEXITY", 15.4)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_structurally_valid"])
        self.assertEqual(res["evaluation_state"], "VALID")
        
        # F1 out of bounds (> 100)
        res_fail = self.nlp.evaluate_metric_bounds("F1", 101.5)
        self.assertFalse(res_fail["is_structurally_valid"])

    def test_tensor2tensor_algebra(self):
        logger.info("Testing OmniTensor2TensorEngine...")
        res = self.t2t.compute_attention_projection(sequence_length=128, num_heads=8, d_model=512)
        self.assertEqual(res["status"], "success")
        # 3 * (512*512 + 512) = 3 * (262144 + 512) = 3 * 262656 = 787968
        self.assertEqual(res["projection_parameters"], 787968)
        self.assertEqual(res["qkv_tensor_shape"], [1, 128, 8, 64])

    def test_nemo_manifest_binding(self):
        logger.info("Testing OmniNemoEngine...")
        res = self.nemo.serialize_nemo_manifest("/path/to/audio/test.wav", 13.52, "hello nemo representation")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["text_length"], 25)
        self.assertEqual(res["nemo_strict_record"]["duration"], 13.52)
        
    def test_manga_image_overlap(self):
        logger.info("Testing OmniMangaImageTranslatorEngine...")
        # Exact intersection bounds
        box1 = [0, 0, 10, 10]
        box2 = [5, 5, 15, 15]
        # Intersection is 5x5 = 25. Total Area = 100 + 100 = 200. Union = 175. IOU = 25/175
        res = self.manga.compute_intersection_over_union(box1, box2)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_overlapping"])
        self.assertAlmostEqual(res["calculated_iou"], 0.142857)

    def test_espnet_conformer_logic(self):
        logger.info("Testing OmniEspnetEngine...")
        res = self.espnet.compute_conformer_complexity(d_model=256, num_heads=4, cnn_kernel_size=15)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["total_mac_architecture_complexity"], 100000)

if __name__ == '__main__':
    print(f"OMNI BATCH 19 SEMESTER 9 - INTEGRATION TESTS STARTING")
    unittest.main(verbosity=2)
