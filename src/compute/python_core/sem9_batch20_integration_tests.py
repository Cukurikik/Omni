import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH20: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_audiolab_engine import OmniAudiolabEngine
from omni_audiomentations_engine import OmniAudiomentationsEngine
from omni_audioshare_engine import OmniAudioShareEngine
from omni_audiowaveform_engine import OmniAudiowaveformEngine
from omni_auto_claude_research_engine import OmniAutoClaudeResearchEngine

class TestOmniBatch20Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 20 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 20 Engines')
        cls.e0 = OmniAudiolabEngine()
        cls.e1 = OmniAudiomentationsEngine()
        cls.e2 = OmniAudioShareEngine()
        cls.e3 = OmniAudiowaveformEngine()
        cls.e4 = OmniAutoClaudeResearchEngine()

    def test_omni_audiolab_engine(self):
        logger.info('Testing OmniAudiolabEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audiomentations_engine(self):
        logger.info('Testing OmniAudiomentationsEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audioshare_engine(self):
        logger.info('Testing OmniAudioShareEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audiowaveform_engine(self):
        logger.info('Testing OmniAudiowaveformEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_auto_claude_research_engine(self):
        logger.info('Testing OmniAutoClaudeResearchEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 20 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
