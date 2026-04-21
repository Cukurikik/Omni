import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH22: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_bento4_engine import OmniBento4Engine
from omni_bertopic_engine import OmniBERTopicEngine
from omni_bertviz_attention_engine import OmniBertVizAttentionEngine
from omni_bitsandbytes_optimizer_engine import OmniBitsAndBytesOptimizerEngine
from omni_black_candy_engine import OmniBlackCandyEngine

class TestOmniBatch22Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 22 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 22 Engines')
        cls.e0 = OmniBento4Engine()
        cls.e1 = OmniBERTopicEngine()
        cls.e2 = OmniBertVizAttentionEngine()
        cls.e3 = OmniBitsAndBytesOptimizerEngine()
        cls.e4 = OmniBlackCandyEngine()

    def test_omni_bento4_engine(self):
        logger.info('Testing OmniBento4Engine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_bertopic_engine(self):
        logger.info('Testing OmniBERTopicEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_bertviz_attention_engine(self):
        logger.info('Testing OmniBertVizAttentionEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_bitsandbytes_optimizer_engine(self):
        logger.info('Testing OmniBitsAndBytesOptimizerEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_black_candy_engine(self):
        logger.info('Testing OmniBlackCandyEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 22 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
