import asyncio
import unittest

from omni_dowhy_causal_engine import OmniDoWhyCausalEngine
from omni_ml_interview_evaluator_engine import OmniMLInterviewEvaluatorEngine
from omni_cortex_model_serving_engine import OmniCortexModelServingEngine
from omni_bertviz_attention_engine import OmniBertVizAttentionEngine
from omni_tensorboardx_logger_engine import OmniTensorboardXLoggerEngine

class TestSem8Batch2Engines(unittest.IsolatedAsyncioTestCase):
    
    # --- DoWhy ---
    async def test_dowhy_initialization(self):
        engine = OmniDoWhyCausalEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_dowhy_process(self):
        engine = OmniDoWhyCausalEngine()
        await engine.initialize()
        res = await engine.process({
            "treatment": "medication",
            "outcome": "recovery",
            "confounders": ["age", "weight"]
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("model_id", res["data"])
        self.assertIn("results", res["data"])
        
    # --- ML Interview ---
    async def test_ml_interview_initialization(self):
        engine = OmniMLInterviewEvaluatorEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_ml_interview_process(self):
        engine = OmniMLInterviewEvaluatorEngine()
        await engine.initialize()
        res = await engine.process({
            "category": "system_design",
            "complexity": 5,
            "response": "A highly detailed long structured response over many words " * 20
        })
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["data"]["evaluation"]["passed"])
        
    # --- Cortex ---
    async def test_cortex_initialization(self):
        engine = OmniCortexModelServingEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_cortex_deploy_and_infer(self):
        engine = OmniCortexModelServingEngine()
        await engine.initialize()
        
        # Deploy
        d_res = await engine.process({"operation": "deploy", "api_name": "test-api", "model_path": "s3://models/xyz"})
        self.assertEqual(d_res["status"], "success")
        
        # Infer
        i_res = await engine.process({"operation": "infer", "api_name": "test-api", "payload": [1,2,3]})
        self.assertEqual(i_res["status"], "success")
        
    # --- BertViz ---
    async def test_bertviz_initialization(self):
        engine = OmniBertVizAttentionEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_bertviz_process(self):
        engine = OmniBertVizAttentionEngine()
        await engine.initialize()
        res = await engine.process({"tokens": ["Hello", "World"], "layers": 2, "heads": 2})
        self.assertEqual(res["status"], "success")
        self.assertIn("visualization_payload", res["data"])
        
    # --- TensorboardX ---
    async def test_tensorboardx_initialization(self):
        engine = OmniTensorboardXLoggerEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_tensorboardx_process(self):
        engine = OmniTensorboardXLoggerEngine()
        await engine.initialize()
        res = await engine.process({"operation": "scalar", "tag": "loss", "value": 0.5, "global_step": 1})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["data"]["wrote"], "scalar")

if __name__ == "__main__":
    unittest.main()
