import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from compute.python_core.omni_henry_awesome_multimodal_llm_engine import OmniHenryAwesomeMultimodalLlmEngine
from compute.python_core.omni_colpali_cookbooks_engine import OmniColpaliCookbooksEngine
from compute.python_core.omni_scientific_llm_survey_engine import OmniScientificLlmSurveyEngine
from compute.python_core.omni_block_bootstrap_pytorch_engine import OmniBlockBootstrapPytorchEngine
from compute.python_core.omni_awesome_efficient_lrm_reasoning_engine import OmniAwesomeEfficientLrmReasoningEngine
from compute.python_core.omni_r1_vl_engine import OmniR1VlEngine
from compute.python_core.omni_cmu_multimodalsdk_engine import OmniCmuMultimodalsdkEngine
from compute.python_core.omni_ma_lmm_engine import OmniMaLmmEngine
from compute.python_core.omni_glm_skills_engine import OmniGlmSkillsEngine
from compute.python_core.omni_multimodalrag_engine import OmniMultimodalragEngine


class TestSemester12Batch13(unittest.TestCase):
    def setUp(self):
        self.config = {"test_mode": True}

    def test_henry_awesome_multimodal_llm_engine(self):
        engine = OmniHenryAwesomeMultimodalLlmEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.compute_mllm_score({}).is_success)
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_colpali_cookbooks_engine(self):
        engine = OmniColpaliCookbooksEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.retrieve_colpali_document("img", "query").is_success)

    def test_scientific_llm_survey_engine(self):
        engine = OmniScientificLlmSurveyEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.evaluate_scientific_accuracy("claim").is_success)

    def test_block_bootstrap_pytorch_engine(self):
        engine = OmniBlockBootstrapPytorchEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.construct_block_bootstrap(["x"], 5).is_success)

    def test_awesome_efficient_lrm_reasoning_engine(self):
        engine = OmniAwesomeEfficientLrmReasoningEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.execute_efficient_lrm("prompt").is_success)

    def test_r1_vl_engine(self):
        engine = OmniR1VlEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.compute_r1_vision_reasoning("img", "task").is_success)

    def test_cmu_multimodalsdk_engine(self):
        engine = OmniCmuMultimodalsdkEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.align_cmu_multimodal([], []).is_success)

    def test_ma_lmm_engine(self):
        engine = OmniMaLmmEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.answer_long_video("vid", "q").is_success)

    def test_glm_skills_engine(self):
        engine = OmniGlmSkillsEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.trigger_glm_skill("inst").is_success)

    def test_multimodalrag_engine(self):
        engine = OmniMultimodalragEngine(self.config)
        self.assertTrue(engine.initialize().is_success)
        self.assertTrue(engine.execute_multimodal_rag("q", []).is_success)


if __name__ == '__main__':
    unittest.main()
