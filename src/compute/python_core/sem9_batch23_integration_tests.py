import os, sys, unittest, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BATCH23: %(message)s")
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from omni_bmt_engine import OmniBmtEngine
from omni_boss_sensor_anomaly_engine import OmniBossSensorAnomalyEngine
from omni_boss_sensor_engine import OmniBossSensorEngine
from omni_boxmot_engine import OmniBoxMOTEngine
from omni_caffe_legacy_bridge_engine import OmniCaffeLegacyBridgeEngine

class TestOmniBatch23Integration(unittest.TestCase):
    """Integration Tests for OMNI Semester 9 Batch 23 Engines."""
    @classmethod
    def setUpClass(cls):
        logger.info('Initializing Batch 23 Engines')
        cls.e0 = OmniBmtEngine()
        cls.e1 = OmniBossSensorAnomalyEngine()
        cls.e2 = OmniBossSensorEngine()
        cls.e3 = OmniBoxMOTEngine()
        cls.e4 = OmniCaffeLegacyBridgeEngine()

    def test_omni_bmt_engine(self):
        logger.info('Testing OmniBmtEngine...')
        diag = self.e0.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_boss_sensor_anomaly_engine(self):
        logger.info('Testing OmniBossSensorAnomalyEngine...')
        diag = self.e1.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_boss_sensor_engine(self):
        logger.info('Testing OmniBossSensorEngine...')
        diag = self.e2.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_boxmot_engine(self):
        logger.info('Testing OmniBoxMOTEngine...')
        diag = self.e3.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

    def test_omni_caffe_legacy_bridge_engine(self):
        logger.info('Testing OmniCaffeLegacyBridgeEngine...')
        diag = self.e4.diagnostics()
        self.assertIsInstance(diag, dict)
        has_status = any(k in diag for k in ['status', 'state', 'health'])
        self.assertTrue(has_status, f'No status key in diag: {list(diag.keys())}')

if __name__ == '__main__':
    print(f'OMNI BATCH 23 SEMESTER 9 - INTEGRATION TESTS STARTING')
    unittest.main(verbosity=2)
