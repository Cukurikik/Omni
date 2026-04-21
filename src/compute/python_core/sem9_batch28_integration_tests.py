import os
import sys
import unittest
import logging
from typing import Dict, Any

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] OMNI_INTEGRATION_TEST_BATCH28: %(message)s")
logger = logging.getLogger(__name__)

# Dynamically add the compute domain path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from omni_bayling_engine import OmniBaylingEngine
from omni_bitextor_engine import OmniBitextorEngine
from omni_stopes_engine import OmniStopesEngine
from omni_bleualign_engine import OmniBleualignEngine

class TestOmniBatch28Integration(unittest.TestCase):
    """
    Integration Tests for OMNI Semester 9 Batch 28 Engines.
    Validates dimensional boundary calculations reliably natively.
    """

    @classmethod
    def setUpClass(cls):
        logger.info("Initializing Batch 28 Engines for Integration Testing")
        cls.bayling = OmniBaylingEngine()
        cls.bitextor = OmniBitextorEngine()
        cls.stopes = OmniStopesEngine()
        cls.bleualign = OmniBleualignEngine()

    def test_bayling_quantization_bounds(self):
        logger.info("Testing OmniBaylingEngine...")
        # bill=7, int8=True, ctx=4096
        # mult = 1
        # base = 7 * 10^9 * 1 = 7000000000
        # cache = 4096 * 1024 * 64 * 2 = 536870912
        # ttl = 7536870912
        res = self.bayling.limit_quantized_llama_overhead(7, True, 4096)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["base_model_quantized_limit_bytes"], 7000000000)
        self.assertEqual(res["absolute_instruction_translation_bytes"], 7536870912)

    def test_bitextor_warc_geometry(self):
        logger.info("Testing OmniBitextorEngine...")
        # cd=100, node=500, str=10000
        # dom = 100 * 500 * 64 = 3200000
        # cp = 10000 * 32 = 320000
        # match = (100 * 10000) // 100 = 10000
        # ttl = 3530000
        res = self.bitextor.evaluate_structural_warc_document_geometry(100, 500, 10000)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["parallel_dom_tree_memory_bytes"], 3200000)
        self.assertEqual(res["absolute_warc_alignment_bytes"], 3530000)

    def test_stopes_cluster_bounds(self):
        logger.info("Testing OmniStopesEngine...")
        # slurm=10, jobs=50, dep=200
        # state = 10 * 50 * 4096 = 2048000
        # dag = 200 * 200 * 8 = 320000
        # ttl = 2368000
        res = self.stopes.map_cluster_job_boundaries(10, 50, 200)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["dependency_dag_resolution_overhead_bytes"], 320000)
        self.assertEqual(res["absolute_orchestration_overhead_bytes"], 2368000)

    def test_bleualign_dp_matrix(self):
        logger.info("Testing OmniBleualignEngine...")
        # left=1000, right=1200
        # grid = 1000 * 1200 * 4 = 4800000
        # back = (1000 + 1200) * 8 = 17600
        # ttl = 4817600
        res = self.bleualign.matrix_dp_sentence_alignment(1000, 1200)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["alignment_nxm_grid_logic_bytes"], 4800000)
        self.assertEqual(res["absolute_bleualign_memory_limit_bytes"], 4817600)

if __name__ == '__main__':
    print(f"OMNI BATCH 28 SEMESTER 9 - INTEGRATION TESTS STARTING")
    unittest.main(verbosity=2)
