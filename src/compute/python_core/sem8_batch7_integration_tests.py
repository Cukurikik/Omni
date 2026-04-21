import asyncio
import unittest

from omni_autoscraper_engine import OmniAutoscraperEngine
from omni_pyprobml_engine import OmniPyProbMLEngine
from omni_serpent_ai_engine import OmniSerpentAIEngine
from omni_coreml_models_engine import OmniCoreMLModelsEngine
from omni_fun_rec_engine import OmniFunRecEngine

class TestSem8Batch7Engines(unittest.IsolatedAsyncioTestCase):
    
    # --- AutoScraper ---
    async def test_autoscraper_initialization(self):
        engine = OmniAutoscraperEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_autoscraper_process(self):
        engine = OmniAutoscraperEngine()
        await engine.initialize()
        res = await engine.process({"complexity_scalar": 200, "strict_mode": True})
        self.assertEqual(res["status"], "success")
        data = res["data"]["dom_extraction_metrics"]
        self.assertEqual(data["synthetic_dom_complexity"], 200)
        self.assertEqual(data["extraction_confidence"], 0.95)
        
    # --- PyProbML ---
    async def test_pyprobml_initialization(self):
        engine = OmniPyProbMLEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_pyprobml_process(self):
        engine = OmniPyProbMLEngine()
        await engine.initialize()
        res = await engine.process({"prior_mean": 0.4, "likelihood_estimate": 0.9, "dimensions": 128})
        self.assertEqual(res["status"], "success")
        data = res["data"]["bayesian_inference"]
        self.assertEqual(data["state_dimensions"], 128)
        
    # --- Serpent AI ---
    async def test_serpent_ai_initialization(self):
        engine = OmniSerpentAIEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_serpent_ai_process(self):
        engine = OmniSerpentAIEngine()
        await engine.initialize()
        res = await engine.process({"frame_density": 0.85, "tick_count": 120})
        self.assertEqual(res["status"], "success")
        data = res["data"]["controller_mapping"]
        self.assertEqual(data["ticks_simulated"], 120)
        self.assertTrue("isolated" not in data["isolation_status"].lower() or "No OS APIs" in data["isolation_status"])
        
    # --- CoreML Models ---
    async def test_coreml_models_initialization(self):
        engine = OmniCoreMLModelsEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_coreml_models_process(self):
        engine = OmniCoreMLModelsEngine()
        await engine.initialize()
        res = await engine.process({"layers": 100, "use_8bit": True})
        self.assertEqual(res["status"], "success")
        data = res["data"]["coreml_edge_projection"]
        self.assertEqual(data["layer_depth_computed"], 100)
        self.assertTrue(data["is_8bit_quantized"])
        
    # --- Fun-Rec ---
    async def test_fun_rec_initialization(self):
        engine = OmniFunRecEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_fun_rec_process(self):
        engine = OmniFunRecEngine()
        await engine.initialize()
        res = await engine.process({"user_count": 1000, "item_pool_size": 5000})
        self.assertEqual(res["status"], "success")
        data = res["data"]["recommendation_retrieval"]
        self.assertEqual(data["users_computed"], 1000)
        self.assertEqual(data["resolved_hit_ratio"], 0.82)

if __name__ == "__main__":
    unittest.main()
