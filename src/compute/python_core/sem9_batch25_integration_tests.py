import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH25: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_camel_roleplaying_agents_engine import OmniCamelRoleplayingAgentsEngine
from omni_causalml_engine import OmniCausalmlEngine
from omni_chinese_clip_engine import OmniChineseClipEngine
from omni_chromaprint_engine import OmniChromaprintEngine
from omni_classical_ml_algorithms_engine import OmniClassicalMlAlgorithmsEngine

class TestOmniBatch25Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 25 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 25 Engines')
        cls.e0 = OmniCamelRoleplayingAgentsEngine()
        cls.e1 = OmniCausalmlEngine()
        cls.e2 = OmniChineseClipEngine()
        cls.e3 = OmniChromaprintEngine()
        cls.e4 = OmniClassicalMlAlgorithmsEngine()

    def test_omni_camel_roleplaying_agents_engine(self):
        logger.info('Testing OmniCamelRoleplayingAgentsEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_causalml_engine(self):
        logger.info('Testing OmniCausalmlEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_chinese_clip_engine(self):
        logger.info('Testing OmniChineseClipEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_chromaprint_engine(self):
        logger.info('Testing OmniChromaprintEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_classical_ml_algorithms_engine(self):
        logger.info('Testing OmniClassicalMlAlgorithmsEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 25 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
