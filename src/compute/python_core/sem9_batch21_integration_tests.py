import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH21: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_auto_editor_engine import OmniAutoEditorEngine
from omni_autoclaude_engine import OmniAutoclaudeEngine
from omni_autoeda_engine import OmniAutoEDAEngine
from omni_autoscraper_engine import OmniAutoscraperEngine
from omni_background_matting_v2_engine import OmniBackgroundMattingV2Engine

class TestOmniBatch21Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 21 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 21 Engines')
        cls.e0 = OmniAutoEditorEngine()
        cls.e1 = OmniAutoclaudeEngine()
        cls.e2 = OmniAutoEDAEngine()
        cls.e3 = OmniAutoscraperEngine()
        cls.e4 = OmniBackgroundMattingV2Engine()

    def test_omni_auto_editor_engine(self):
        logger.info('Testing OmniAutoEditorEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_autoclaude_engine(self):
        logger.info('Testing OmniAutoclaudeEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_autoeda_engine(self):
        logger.info('Testing OmniAutoEDAEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_autoscraper_engine(self):
        logger.info('Testing OmniAutoscraperEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_background_matting_v2_engine(self):
        logger.info('Testing OmniBackgroundMattingV2Engine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 21 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
