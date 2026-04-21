import os
import sys
import unittest
import json
import logging
from typing import Dict, Any

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] OMNI_INTEGRATION_TEST_BATCH16: %(message)s")
logger = logging.getLogger(__name__)

# Dynamically add the compute domain path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from omni_spacy_models_engine import OmniSpacyModelsEngine
from omni_ray_llm_apps_engine import OmniRayLlmAppsEngine
from omni_spago_bridge_engine import OmniSpagoBridgeEngine
from omni_gen_julia_engine import OmniGenJuliaEngine
from omni_gplearn_engine import OmniGPLearnEngine

class TestOmniBatch16Integration(unittest.TestCase):
    """
    Integration Tests for OMNI Semester 9 Batch 16 Engines.
    Tests structural adherence, monadic returns, and domain execution.
    """

    @classmethod
    def setUpClass(cls):
        logger.info("Initializing Batch 16 Engines for Integration Testing")
        cls.spacy = OmniSpacyModelsEngine()
        cls.ray = OmniRayLlmAppsEngine()
        cls.spago = OmniSpagoBridgeEngine()
        cls.genjl = OmniGenJuliaEngine()
        cls.gp = OmniGPLearnEngine()

    def test_spacy_meta_validation(self):
        logger.info("Testing OmniSpacyModelsEngine...")
        diag = self.spacy.diagnostics()
        self.assertEqual(diag.get("status"), "operational")

        meta = {
            "lang": "en",
            "name": "core_web_sm",
            "pipeline": ["tok2vec", "tagger", "parser", "ner"],
            "vectors": {"width": 0}
        }
        res = self.spacy.validate_spacy_meta(meta)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["model_identifier"], "en_core_web_sm")
        self.assertFalse(res["is_vectorized"])

    def test_ray_serve_manifest(self):
        logger.info("Testing OmniRayLlmAppsEngine...")
        res = self.ray.craft_serve_manifest("llama_router", "meta-llama/Llama-2-7b-chat-hf", 4, 1.5)
        self.assertEqual(res["status"], "success")
        
        manifest = res["serve_manifest"]
        self.assertEqual(manifest["name"], "llama_router")
        self.assertEqual(manifest["ray_actor_options"]["num_gpus"], 1.5)
        self.assertEqual(res["total_gpus_required"], 6.0) # 4 replicas * 1.5 GPUs

    def test_spago_tensor_serialization(self):
        logger.info("Testing OmniSpagoBridgeEngine...")
        matrix = [[1.0, 2.0], [3.0, 4.0]]
        res = self.spago.serialize_tensor_graph(matrix, requires_grad=True)
        self.assertEqual(res["status"], "success")
        
        parsed = json.loads(res["spago_json_struct"])
        self.assertEqual(parsed["Type"], "matrix")
        self.assertEqual(parsed["Rows"], 2)
        self.assertEqual(parsed["Cols"], 2)
        self.assertTrue(parsed["RequiresGrad"])

    def test_gen_julia_macro(self):
        logger.info("Testing OmniGenJuliaEngine...")
        res = self.genjl.compile_inference_model([0.5, 1.2, 3.4], 0.1)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["trace_variable_count"], 3)
        self.assertIn("@gen function omni_inferred_model()", res["julia_macro_definition"])

    def test_gplearn_symbolic_evaluation(self):
        logger.info("Testing OmniGPLearnEngine...")
        
        # Target expression: x * (y + 2)
        ast = {
            "op": "mul",
            "left": {"var": "x"},
            "right": {
                "op": "add",
                "left": {"var": "y"},
                "right": {"value": 2.0}
            }
        }
        
        res = self.gp.evaluate_genetic_tree(ast, {"x": 3.0, "y": 4.0})
        self.assertEqual(res["status"], "success")
        # 3 * (4 + 2) = 18.0
        self.assertEqual(res["computed_value"], 18.0)

if __name__ == '__main__':
    print(f"OMNI BATCH 16 SEMESTER 9 - INTEGRATION TESTS STARTING")
    unittest.main(verbosity=2)
