import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBatch9Engines(unittest.TestCase):
    def test_engine_registry_count(self):
        from engines.engine_registry import BATCH9_ENGINES
        self.assertEqual(len(BATCH9_ENGINES), 30)

    def test_all_engine_health_checks(self):
        from engines.omni_core_engines import OmniKVPressEngine, OmniEmbedAnythingEngine, OmniSophiaEngine
        from engines.omni_vision_engines import OmniVisionLLMEngine, OmniPointLLMEngine, OmniXrayGLMEngine, OmniVisCPMEngine, OmniShareGPT4VideoEngine
        from engines.omni_tool_engines import OmniLLMBlenderEngine, OmniLangkitEngine, OmniWebLLMEngine, OmniHackingBuddyEngine, OmniAutoLLMEngine, OmniLLMSandboxEngine
        from engines.omni_domain_engines import OmniQwenMathEngine, OmniCareGPTEngine, OmniLawyerLlamaEngine, OmniLLMPrunerEngine
        from engines.omni_survey_engines import (OmniHallucinationEngine, OmniLLM4IEEngine, OmniGraphLLMEngine,
            OmniPrompt4ReasonEngine, OmniLLMSurveyEngine, OmniLLMAgentEngine, OmniLLMSafetyEngine,
            OmniLLMWorkshopEngine, OmniRolePlayingEngine, OmniFoundationModelsEngine, OmniLLMInferenceEngine, OmniTinyLLMEngine)
        engines = [
            OmniKVPressEngine(), OmniEmbedAnythingEngine(), OmniSophiaEngine(),
            OmniVisionLLMEngine(), OmniPointLLMEngine(), OmniXrayGLMEngine(), OmniVisCPMEngine(), OmniShareGPT4VideoEngine(),
            OmniLLMBlenderEngine(), OmniLangkitEngine(), OmniWebLLMEngine(), OmniHackingBuddyEngine(), OmniAutoLLMEngine(), OmniLLMSandboxEngine(),
            OmniQwenMathEngine(), OmniCareGPTEngine(), OmniLawyerLlamaEngine(), OmniLLMPrunerEngine(),
            OmniHallucinationEngine(), OmniLLM4IEEngine(), OmniGraphLLMEngine(), OmniPrompt4ReasonEngine(),
            OmniLLMSurveyEngine(), OmniLLMAgentEngine(), OmniLLMSafetyEngine(), OmniLLMWorkshopEngine(),
            OmniRolePlayingEngine(), OmniFoundationModelsEngine(), OmniLLMInferenceEngine(), OmniTinyLLMEngine(),
        ]
        for e in engines:
            h = e.health_check()
            self.assertEqual(h["status"], "healthy")
            self.assertTrue(h["engine_id"].endswith("-s14b9"))

    def test_kvpress_compressor(self):
        from compute.kvpress_compressor import KVPress
        import torch
        press = KVPress(0.5)
        keys = torch.randn(1, 4, 100, 64)
        r = press.compress_knorm(keys)
        self.assertTrue(r.is_ok)
        self.assertEqual(r.value.shape[2], 50)  # 50% of 100

    def test_sophia_optimizer_init(self):
        from compute.sophia_optimizer import SophiaG
        import torch
        model = torch.nn.Linear(10, 10)
        opt = SophiaG(model.parameters(), lr=1e-4, rho=0.04)
        self.assertIsNotNone(opt)

    def test_qwen_math_verifier(self):
        from compute.qwen_math_verifier import MathVerifier
        v = MathVerifier()
        r = v.verify_numerical("3.14159", "3.14159")
        self.assertTrue(r.is_ok and r.value)
        r2 = v.extract_boxed_answer("The answer is \\boxed{42}.")
        self.assertTrue(r2.is_ok)
        self.assertEqual(r2.value, "42")

    def test_langkit_analyzer(self):
        from compute.langkit_analyzer import LangkitAnalyzer
        a = LangkitAnalyzer()
        r = a.analyze("This is a test sentence for analysis.")
        self.assertTrue(r.is_ok)
        self.assertIn("word_count", r.value)
        self.assertEqual(r.value["word_count"], 7)

    def test_llm_blender_ranker(self):
        from compute.llm_blender_ranker import PairRMRanker
        ranker = PairRMRanker()
        r = ranker.rank_candidates("test", ["short", "medium length", "very long response here"])
        self.assertTrue(r.is_ok)
        self.assertEqual(len(r.value), 3)

    def test_visionllm_detector(self):
        from compute.visionllm_detector import VisionLLMDetector
        import torch
        det = VisionLLMDetector(80)
        logits = torch.randn(10, 80)
        boxes = torch.rand(10, 4)
        r = det.decode_predictions(logits, boxes, 0.0)
        self.assertTrue(r.is_ok)

if __name__ == "__main__":
    print("=" * 70)
    print("OMNI SEMESTER 14 BATCH 9 — INTEGRATION TEST SUITE")
    print("=" * 70)
    results = {"pass": 0, "fail": 0}
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBatch9Engines)
    for test in suite:
        try:
            test.debug()
            name = str(test).split()[0]
            print(f"  [PASS] {name}")
            results["pass"] += 1
        except Exception as ex:
            name = str(test).split()[0]
            print(f"  [FAIL] {name}: {ex}")
            results["fail"] += 1
    total = results["pass"] + results["fail"]
    print("=" * 70)
    print(f"TOTAL: {total} | PASSED: {results['pass']} | FAILED: {results['fail']}")
    print(f"STATUS: {'ALL PASS' if results['fail'] == 0 else 'HAS FAILURES'}")
    print("=" * 70)
