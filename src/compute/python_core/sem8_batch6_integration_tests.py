import asyncio
import unittest

from omni_deepmind_lab_engine import OmniDeepmindLabEngine
from omni_python_ml_book_engine import OmniPythonMLBookEngine
from omni_ml_specialization_engine import OmniMLSpecializationEngine
from omni_background_matting_v2_engine import OmniBackgroundMattingV2Engine
from omni_guess_js_engine import OmniGuessJSEngine

class TestSem8Batch6Engines(unittest.IsolatedAsyncioTestCase):
    
    # --- DeepMind Lab ---
    async def test_deepmind_lab_initialization(self):
        engine = OmniDeepmindLabEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_deepmind_lab_process(self):
        engine = OmniDeepmindLabEngine()
        await engine.initialize()
        res = await engine.process({"action_vector": [1.0, 0.0, 0.5], "intensity_steps": 10})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["data"]["rl_state"]["steps_processed"], 10)
        self.assertFalse(res["data"]["rl_state"]["episode_terminated"])
        
    # --- Python ML Book ---
    async def test_python_ml_book_initialization(self):
        engine = OmniPythonMLBookEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_python_ml_book_process(self):
        engine = OmniPythonMLBookEngine()
        await engine.initialize()
        res = await engine.process({"algorithm": "adaline", "data_size": 150})
        self.assertEqual(res["status"], "success")
        data = res["data"]["foundational_metric"]
        self.assertEqual(data["algorithm_used"], "adaline")
        self.assertEqual(data["synthetic_accuracy"], 0.95)
        
    # --- ML Specialization ---
    async def test_ml_specialization_initialization(self):
        engine = OmniMLSpecializationEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_ml_specialization_process(self):
        engine = OmniMLSpecializationEngine()
        await engine.initialize()
        res = await engine.process({"learning_rate": 0.01, "steps": 500})
        self.assertEqual(res["status"], "success")
        data = res["data"]["optimization_manifold"]
        self.assertTrue(data["global_optimum_reached"])
        
    # --- Background Matting V2 ---
    async def test_background_matting_initialization(self):
        engine = OmniBackgroundMattingV2Engine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_background_matting_process(self):
        engine = OmniBackgroundMattingV2Engine()
        await engine.initialize()
        res = await engine.process({"width": 1920, "height": 1080, "has_background": True})
        self.assertEqual(res["status"], "success")
        data = res["data"]["cv_matting"]
        self.assertEqual(data["pixels_mapped"], 1920*1080)
        self.assertEqual(data["matting_efficiency"], 0.99)
        
    # --- Guess JS ---
    async def test_guess_js_initialization(self):
        engine = OmniGuessJSEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_guess_js_process(self):
        engine = OmniGuessJSEngine()
        await engine.initialize()
        res = await engine.process({"current_route": "/home", "historical_points": 50})
        self.assertEqual(res["status"], "success")
        data = res["data"]["predictive_route_map"]
        self.assertEqual(data["current_node"], "/home")
        self.assertEqual(len(data["highest_probability_routes"]), 3)

if __name__ == "__main__":
    unittest.main()
