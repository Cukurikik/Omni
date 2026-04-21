import asyncio
import unittest

from omni_smile_engine import OmniSmileEngine
from omni_pytorch_metric_learning_engine import OmniPytorchMetricLearningEngine
from omni_lihang_stat_learning_engine import OmniLihangStatLearningEngine
from omni_tensorpack_engine import OmniTensorpackEngine
from omni_swarms_engine import OmniSwarmsEngine

class TestSem8Batch9Engines(unittest.IsolatedAsyncioTestCase):
    
    # --- Smile ---
    async def test_smile_initialization(self):
        engine = OmniSmileEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_smile_process(self):
        engine = OmniSmileEngine()
        await engine.initialize()
        # Evaluate relatively small native tree
        res = await engine.process({"samples": 100, "features": 5, "trees": 10})
        self.assertEqual(res["status"], "success")
        data = res["data"]["smile_statistical_projection"]
        self.assertEqual(data["samples_evaluated"], 100)
        
    # --- PyTorch Metric Learning ---
    async def test_pytorch_metric_learning_initialization(self):
        engine = OmniPytorchMetricLearningEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_pytorch_metric_learning_process(self):
        engine = OmniPytorchMetricLearningEngine()
        await engine.initialize()
        res = await engine.process({"batch_size": 16, "embedding_dim": 64, "loss_type": "triplet"})
        self.assertEqual(res["status"], "success")
        data = res["data"]["metric_representation_projection"]
        self.assertTrue("native_loss_value" in data)
        self.assertEqual(data["loss_function_deployed"], "TripletMarginLoss")
        
    # --- Lihang Statistical Learning ---
    async def test_lihang_initialization(self):
        engine = OmniLihangStatLearningEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_lihang_process(self):
        engine = OmniLihangStatLearningEngine()
        await engine.initialize()
        res = await engine.process({"samples": 100, "dimensions": 5, "epochs": 20})
        self.assertEqual(res["status"], "success")
        data = res["data"]["statistical_representation"]
        self.assertTrue(isinstance(data["learned_bias_output"], float))
        
    # --- Tensorpack ---
    async def test_tensorpack_initialization(self):
        engine = OmniTensorpackEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_tensorpack_process(self):
        engine = OmniTensorpackEngine()
        await engine.initialize()
        res = await engine.process({"dataset_size": 20, "batch_size": 5})
        self.assertEqual(res["status"], "success")
        data = res["data"]["dataflow_representation"]
        self.assertEqual(data["total_yielded_batches"], 4)
        
    # --- Swarms ---
    async def test_swarms_initialization(self):
        engine = OmniSwarmsEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_swarms_process(self):
        engine = OmniSwarmsEngine()
        await engine.initialize()
        res = await engine.process({"num_agents": 2})
        self.assertEqual(res["status"], "success")
        data = res["data"]["swarm_representation"]
        self.assertEqual(data["agents_constructed"], 2)
        self.assertTrue(data["nodes_memory_mounted"])

if __name__ == "__main__":
    unittest.main()
