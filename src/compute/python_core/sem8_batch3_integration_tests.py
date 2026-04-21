import asyncio
import unittest

from omni_librephotos_gallery_engine import OmniLibrePhotosGalleryEngine
from omni_ml_yearning_strategy_engine import OmniMLYearningStrategyEngine
from omni_stanza_linguistics_engine import OmniStanzaLinguisticsEngine
from omni_featuretools_engineering_engine import OmniFeaturetoolsEngineeringEngine
from omni_deeplearning_algorithms_engine import OmniDeepLearningAlgorithmsEngine

class TestSem8Batch3Engines(unittest.IsolatedAsyncioTestCase):
    
    # --- LibrePhotos ---
    async def test_librephotos_initialization(self):
        engine = OmniLibrePhotosGalleryEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_librephotos_indexing(self):
        engine = OmniLibrePhotosGalleryEngine()
        await engine.initialize()
        res = await engine.process({
            "operation": "index",
            "image_id": "img_001",
            "tags": ["person_alice", "outdoor"]
        })
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["data"]["details"]["faces_detected"], 1)
        
    # --- ML Yearning ---
    async def test_ml_yearning_initialization(self):
        engine = OmniMLYearningStrategyEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_ml_yearning_process(self):
        engine = OmniMLYearningStrategyEngine()
        await engine.initialize()
        res = await engine.process({
            "human_error": 1.0,
            "training_error": 5.0,
            "dev_error": 10.0
        })
        self.assertEqual(res["status"], "success")
        strategy = res["data"]["strategy_evaluation"]
        self.assertTrue(strategy["avoidable_bias"] > 2.0)
        self.assertTrue(strategy["variance"] > 2.0)
        
    # --- Stanza ---
    async def test_stanza_initialization(self):
        engine = OmniStanzaLinguisticsEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_stanza_process(self):
        engine = OmniStanzaLinguisticsEngine()
        await engine.initialize()
        res = await engine.process({"text": "Alice went to Paris in France."})
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["data"]["nlp_results"]["token_count"] > 0)
        
    # --- Featuretools ---
    async def test_featuretools_initialization(self):
        engine = OmniFeaturetoolsEngineeringEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_featuretools_process(self):
        engine = OmniFeaturetoolsEngineeringEngine()
        await engine.initialize()
        res = await engine.process({"base_entity": "users", "relationships": 2, "max_depth": 2})
        self.assertEqual(res["status"], "success")
        data = res["data"]["dfs_results"]
        self.assertEqual(data["base_entity"], "users")
        self.assertTrue(len(data["feature_samples"]) > 0)
        
    # --- DeepLearning Core ---
    async def test_deeplearning_initialization(self):
        engine = OmniDeepLearningAlgorithmsEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_deeplearning_process(self):
        engine = OmniDeepLearningAlgorithmsEngine()
        await engine.initialize()
        res = await engine.process({"architecture": "cnn", "epochs": 10})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["data"]["validation"]["epochs_run"], 10)

if __name__ == "__main__":
    unittest.main()
