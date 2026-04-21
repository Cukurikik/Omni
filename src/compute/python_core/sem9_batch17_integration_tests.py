import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH17: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_audio_dev_tools_engine import OmniAudioDevToolsEngine
from omni_audio_gpt_engine import OmniAudioGPTEngine
from omni_audio_library_engine import OmniAudioLibraryEngine
from omni_audio_separator_engine import OmniAudioSeparatorEngine
from omni_audiokit_engine import OmniAudioKitEngine

class TestOmniBatch17Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 17 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 17 Engines')
        cls.e0 = OmniAudioDevToolsEngine()
        cls.e1 = OmniAudioGPTEngine()
        cls.e2 = OmniAudioLibraryEngine()
        cls.e3 = OmniAudioSeparatorEngine()
        cls.e4 = OmniAudioKitEngine()

    def test_omni_audio_dev_tools_engine(self):
        logger.info('Testing OmniAudioDevToolsEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audio_gpt_engine(self):
        logger.info('Testing OmniAudioGPTEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audio_library_engine(self):
        logger.info('Testing OmniAudioLibraryEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audio_separator_engine(self):
        logger.info('Testing OmniAudioSeparatorEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audiokit_engine(self):
        logger.info('Testing OmniAudioKitEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 17 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
