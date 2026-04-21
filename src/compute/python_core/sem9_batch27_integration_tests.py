import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH27: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_clear_mlops_engine import OmniClearMlOpsEngine
from omni_clearer_voice_studio_engine import OmniClearerVoiceStudioEngine
from omni_clearml_mlops_tracker_engine import OmniClearmlMlopsTrackerEngine
from omni_clip_embedding_engine import OmniClipEmbeddingEngine
from omni_coreml_models_engine import OmniCoreMLModelsEngine

class TestOmniBatch27Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 27 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 27 Engines')
        cls.e0 = OmniClearMlOpsEngine()
        cls.e1 = OmniClearerVoiceStudioEngine()
        cls.e2 = OmniClearmlMlopsTrackerEngine()
        cls.e3 = OmniClipEmbeddingEngine()
        cls.e4 = OmniCoreMLModelsEngine()

    def test_omni_clear_mlops_engine(self):
        logger.info('Testing OmniClearMlOpsEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_clearer_voice_studio_engine(self):
        logger.info('Testing OmniClearerVoiceStudioEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_clearml_mlops_tracker_engine(self):
        logger.info('Testing OmniClearmlMlopsTrackerEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_clip_embedding_engine(self):
        logger.info('Testing OmniClipEmbeddingEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_coreml_models_engine(self):
        logger.info('Testing OmniCoreMLModelsEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 27 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
