import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH30: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_daily_cv_engine import OmniDailyCvEngine
from omni_dalle2_image_gen_engine import OmniDalle2ImageGenEngine
from omni_darknet_yolo_engine import OmniDarknetYoloEngine
from omni_data_science_roadmap_engine import OmniDataScienceRoadmapEngine
from omni_datasci_workflow_engine import OmniDatasciWorkflowEngine

class TestOmniBatch30Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 30 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 30 Engines')
        cls.e0 = OmniDailyCvEngine()
        cls.e1 = OmniDalle2ImageGenEngine()
        cls.e2 = OmniDarknetYoloEngine()
        cls.e3 = OmniDataScienceRoadmapEngine()
        cls.e4 = OmniDatasciWorkflowEngine()

    def test_omni_daily_cv_engine(self):
        logger.info('Testing OmniDailyCvEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_dalle2_image_gen_engine(self):
        logger.info('Testing OmniDalle2ImageGenEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_darknet_yolo_engine(self):
        logger.info('Testing OmniDarknetYoloEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_data_science_roadmap_engine(self):
        logger.info('Testing OmniDataScienceRoadmapEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_datasci_workflow_engine(self):
        logger.info('Testing OmniDatasciWorkflowEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 30 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
