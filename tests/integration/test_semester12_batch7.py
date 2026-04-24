import unittest
from src.compute.python_core.omni_parlor_engine import OmniParlorEngine
from src.compute.python_core.omni_pixeltable_engine import OmniPixeltableEngine
from src.compute.python_core.omni_thepipe_engine import OmniThepipeEngine
from src.compute.python_core.omni_multimodal_gpt_engine import OmniMultimodalGptEngine
from src.compute.python_core.omni_mllm_engine import OmniMllmEngine
from src.compute.python_core.omni_ovis_engine import OmniOvisEngine
from src.compute.python_core.omni_awesome_multimodal_research_engine import OmniAwesomeMultimodalResearchEngine
from src.compute.python_core.omni_awesome_japanese_llm_engine import OmniAwesomeJapaneseLlmEngine
from src.compute.python_core.omni_sdt_engine import OmniSdtEngine
from src.compute.python_core.omni_mmpose_engine import OmniMmposeEngine

class TestSemester12Batch7(unittest.TestCase):
    def test_parlor_engine(self):
        engine = OmniParlorEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniParlorEngine")
        
        res = engine.start_conversation("hello")
        self.assertTrue(res.is_ok())
        
    def test_pixeltable_engine(self):
        engine = OmniPixeltableEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniPixeltableEngine")
        
        res = engine.execute_ml_query("SELECT *")
        self.assertTrue(res.is_ok())

    def test_thepipe_engine(self):
        engine = OmniThepipeEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniThepipeEngine")
        
        res = engine.extract_content("http://test.com")
        self.assertTrue(res.is_ok())

    def test_multimodal_gpt_engine(self):
        engine = OmniMultimodalGptEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniMultimodalGptEngine")
        
        res = engine.chat_multimodal("image", "query")
        self.assertTrue(res.is_ok())

    def test_mllm_engine(self):
        engine = OmniMllmEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniMllmEngine")
        
        res = engine.run_fast_inference("instruction")
        self.assertTrue(res.is_ok())

    def test_ovis_engine(self):
        engine = OmniOvisEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniOvisEngine")
        
        res = engine.process_visual_instruction("cmd", "context")
        self.assertTrue(res.is_ok())

    def test_awesome_multimodal_research_engine(self):
        engine = OmniAwesomeMultimodalResearchEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniAwesomeMultimodalResearchEngine")
        
        res = engine.query_multimodal_papers("research")
        self.assertTrue(res.is_ok())

    def test_awesome_japanese_llm_engine(self):
        engine = OmniAwesomeJapaneseLlmEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniAwesomeJapaneseLlmEngine")
        
        res = engine.evaluate_japanese_prompts("data.json")
        self.assertTrue(res.is_ok())

    def test_sdt_engine(self):
        engine = OmniSdtEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniSdtEngine")
        
        res = engine.track_spatial_temporal("tensor")
        self.assertTrue(res.is_ok())

    def test_mmpose_engine(self):
        engine = OmniMmposeEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniMmposeEngine")
        
        res = engine.estimate_pose("tensor")
        self.assertTrue(res.is_ok())

if __name__ == '__main__':
    unittest.main()
