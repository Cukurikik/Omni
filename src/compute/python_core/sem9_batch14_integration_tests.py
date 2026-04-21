import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH14: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_ai_audio_datasets_engine import OmniAIAudioDatasetsEngine
from omni_albumentations_augmentation_engine import OmniAlbumentationsAugmentationEngine
from omni_allennlp_framework_engine import OmniAllennlpFrameworkEngine
from omni_alpaca_instruct_engine import OmniAlpacaInstructEngine
from omni_android_audio_converter_engine import OmniAndroidAudioConverterEngine

class TestOmniBatch14Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 14 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 14 Engines')
        cls.e0 = OmniAIAudioDatasetsEngine()
        cls.e1 = OmniAlbumentationsAugmentationEngine()
        cls.e2 = OmniAllennlpFrameworkEngine()
        cls.e3 = OmniAlpacaInstructEngine()
        cls.e4 = OmniAndroidAudioConverterEngine()

    def test_omni_ai_audio_datasets_engine(self):
        logger.info('Testing OmniAIAudioDatasetsEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_albumentations_augmentation_engine(self):
        logger.info('Testing OmniAlbumentationsAugmentationEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_allennlp_framework_engine(self):
        logger.info('Testing OmniAllennlpFrameworkEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_alpaca_instruct_engine(self):
        logger.info('Testing OmniAlpacaInstructEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_android_audio_converter_engine(self):
        logger.info('Testing OmniAndroidAudioConverterEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 14 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
