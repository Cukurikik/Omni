import os
import sys
import unittest
import json
import logging
from typing import Dict, Any

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] OMNI_INTEGRATION_TEST_BATCH18: %(message)s")
logger = logging.getLogger(__name__)

# Dynamically add the compute domain path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from omni_alan_sdk_flutter_bridge_engine import OmniAlanSdkFlutterBridgeEngine
from omni_top_deep_learning_engine import OmniTopDeepLearningEngine
from omni_ai_security_learning_engine import OmniAiSecurityLearningEngine
from omni_model_db_engine import OmniModelDbEngine

class TestOmniBatch18Integration(unittest.TestCase):
    """
    Integration Tests for OMNI Semester 9 Batch 18 Engines.
    Tests analytical matrices, distance geometry, and structural Flutter integration.
    """

    @classmethod
    def setUpClass(cls):
        logger.info("Initializing Batch 18 Engines for Integration Testing")
        cls.flutter = OmniAlanSdkFlutterBridgeEngine()
        cls.top_dl = OmniTopDeepLearningEngine()
        cls.cyber = OmniAiSecurityLearningEngine()
        cls.modeldb = OmniModelDbEngine()

    def test_flutter_method_channel(self):
        logger.info("Testing OmniAlanSdkFlutterBridgeEngine...")
        res = self.flutter.craft_dart_method_call("com.alan.sdk", "playText", {"text": "Hello"})
        self.assertEqual(res["status"], "success")
        parsed = json.loads(res["serialized_buffer"])
        self.assertEqual(parsed["MethodChannel"], "com.alan.sdk")
        self.assertEqual(parsed["MethodCall"], "playText")
        self.assertEqual(parsed["NativeBridge"], "DartVM")

    def test_top_deep_learning_params(self):
        logger.info("Testing OmniTopDeepLearningEngine...")
        # 1. Image 3D -> Conv2D (filters=32, kernel=3) -> Dense (units=10)
        # Assuming generic topology mapping
        input_shape = [28, 28, 3]
        layers = [
            {"type": "conv2d", "filters": 32, "kernel_size": 3},
            {"type": "dense", "units": 10}
        ]
        res = self.top_dl.evaluate_model_topology(input_shape, layers)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["layer_depth"], 2)
        # Conv2D: (3*3*3)*32 + 32 = 27*32 + 32 = 864 + 32 = 896 Params
        # Dense (from 32 filters mapped logic): 32 * 10 + 10 = 330
        # Total = 896 + 330 = 1226
        self.assertEqual(res["total_parameters"], 1226)

    def test_cybersecurity_anomaly(self):
        logger.info("Testing OmniAiSecurityLearningEngine...")
        feature_vector = [1.5, 2.0, 7.5]
        baseline_vector = [1.0, 2.0, 3.0]
        # Diff: [0.5, 0.0, 4.5] -> Sq: 0.25 + 0.0 + 20.25 = 20.5
        res = self.cyber.compute_anomaly_threshold(feature_vector, baseline_vector)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["squared_euclidean_distance"], 20.5)
        self.assertFalse(res["is_anomaly"]) # Since 20.5 < 25.0

    def test_model_db_grpc_payload(self):
        logger.info("Testing OmniModelDbEngine...")
        params = {"learning_rate": 0.001, "epochs": 50}
        sha = "1234567890123456789012345678901234567890" # 40 chars exactly
        res = self.modeldb.serialize_grpc_commit("project_xyz", params, sha)
        self.assertEqual(res["status"], "success")
        
        payload = res["grpc_payload"]
        self.assertEqual(payload["project_identifier"], "project_xyz")
        self.assertEqual(payload["code_version"]["repository_sha"], sha)
        
        hyper_struct = payload["hyper_parameters_struct"]
        self.assertEqual(len(hyper_struct), 2)
        self.assertEqual(hyper_struct[0]["value_type"], "float")

if __name__ == '__main__':
    print(f"OMNI BATCH 18 SEMESTER 9 - INTEGRATION TESTS STARTING")
    unittest.main(verbosity=2)
