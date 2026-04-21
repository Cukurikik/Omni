import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH29: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_cortex_model_serving_engine import OmniCortexModelServingEngine
from omni_ctranslate2_engine import OmniCTranslate2Engine
from omni_cv_paper_assimilation_engine import OmniCvPaperAssimilationEngine
from omni_cvat_orchestration_engine import OmniCvatOrchestrationEngine
from omni_daft_engine import OmniDaftEngine

class TestOmniBatch29Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 29 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 29 Engines')
        cls.e0 = OmniCortexModelServingEngine()
        cls.e1 = OmniCTranslate2Engine()
        cls.e2 = OmniCvPaperAssimilationEngine()
        cls.e3 = OmniCvatOrchestrationEngine()
        cls.e4 = OmniDaftEngine()

    def test_omni_cortex_model_serving_engine(self):
        logger.info('Testing OmniCortexModelServingEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_ctranslate2_engine(self):
        logger.info('Testing OmniCTranslate2Engine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_cv_paper_assimilation_engine(self):
        logger.info('Testing OmniCvPaperAssimilationEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_cvat_orchestration_engine(self):
        logger.info('Testing OmniCvatOrchestrationEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_daft_engine(self):
        logger.info('Testing OmniDaftEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 29 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
