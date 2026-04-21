import asyncio
import unittest

from omni_vowpal_wabbit_engine import OmniVowpalWabbitEngine
from omni_mage_data_pipeline_engine import OmniMageDataPipelineEngine
from omni_embedded_toolchain_engine import OmniEmbeddedToolchainEngine
from omni_bitsandbytes_optimizer_engine import OmniBitsAndBytesOptimizerEngine
from omni_boxmot_engine import OmniBoxMOTEngine

class TestSem8Batch1Engines(unittest.IsolatedAsyncioTestCase):
    
    async def test_vowpal_wabbit_initialization(self):
        engine = OmniVowpalWabbitEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        self.assertEqual(engine.diagnostics()["status"], "active")
        
    async def test_vowpal_wabbit_process(self):
        engine = OmniVowpalWabbitEngine({"learning_rate": 0.5})
        await engine.initialize()
        res = await engine.process({"operation": "train", "features": [1.0, 0.5], "label": 1.0})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["data"]["action"], "model_updated")
        
    async def test_mage_pipeline_initialization(self):
        engine = OmniMageDataPipelineEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_mage_pipeline_process(self):
        engine = OmniMageDataPipelineEngine()
        await engine.initialize()
        blocks = [{"type": "loader"}, {"type": "transformer"}]
        res = await engine.process({"pipeline_name": "test_pipe", "blocks": blocks})
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["data"]["block_results"]), 2)
        
    async def test_embedded_toolchain_initialization(self):
        engine = OmniEmbeddedToolchainEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_embedded_toolchain_process(self):
        engine = OmniEmbeddedToolchainEngine()
        await engine.initialize()
        res = await engine.process({
            "operation": "build",
            "source_code": "int main() { return 0; }",
            "architecture": "arm-none-eabi"
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("binary_size_bytes", res["data"])
        
    async def test_bitsandbytes_optimizer_initialization(self):
        engine = OmniBitsAndBytesOptimizerEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_bitsandbytes_optimizer_process(self):
        engine = OmniBitsAndBytesOptimizerEngine()
        await engine.initialize()
        res = await engine.process({"operation": "quantize", "tensor_size": 2048})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["data"]["dtype"], "int8")
        
    async def test_boxmot_tracker_initialization(self):
        engine = OmniBoxMOTEngine({"tracker": "DeepOCSORT"})
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")
        
    async def test_boxmot_tracker_process(self):
        engine = OmniBoxMOTEngine({"tracker": "BoTSORT"})
        await engine.initialize()
        detections = [{"bbox": [10, 10, 20, 20], "conf": 0.9}]
        res = await engine.process({"frame_id": 1, "detections": detections})
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["data"]["tracked_objects"]), 1)
        self.assertIn("track_id", res["data"]["tracked_objects"][0])

if __name__ == "__main__":
    unittest.main()
