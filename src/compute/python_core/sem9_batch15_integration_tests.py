import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH15: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_anylabeling_segmentation_engine import OmniAnylabelingSegmentationEngine
from omni_attention_transformer_core_engine import OmniAttentionTransformerCoreEngine
from omni_audacity_editor_engine import OmniAudacityEditorEngine
from omni_audio_analysis_engine import OmniAudioAnalysisEngine
from omni_audio_dataset_engine import OmniAudioDatasetEngine

class TestOmniBatch15Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 15 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 15 Engines')
        cls.e0 = OmniAnylabelingSegmentationEngine()
        cls.e1 = OmniAttentionTransformerCoreEngine()
        cls.e2 = OmniAudacityEditorEngine()
        cls.e3 = OmniAudioAnalysisEngine()
        cls.e4 = OmniAudioDatasetEngine()

    def test_omni_anylabeling_segmentation_engine(self):
        logger.info('Testing OmniAnylabelingSegmentationEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_attention_transformer_core_engine(self):
        logger.info('Testing OmniAttentionTransformerCoreEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audacity_editor_engine(self):
        logger.info('Testing OmniAudacityEditorEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audio_analysis_engine(self):
        logger.info('Testing OmniAudioAnalysisEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_audio_dataset_engine(self):
        logger.info('Testing OmniAudioDatasetEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 15 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
