import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBatch10Engines(unittest.TestCase):
    def test_engine_registry_count(self):
        from engines.engine_registry import BATCH10_ENGINES
        self.assertEqual(len(BATCH10_ENGINES), 30)

    def test_all_engine_health_checks(self):
        from engines.omni_vision_engines import OmniChatUniViEngine, OmniMedicalMultimodalEngine, OmniEagleEngine, OmniStableDiffEngine, OmniControlNetEngine
        from engines.omni_agent_engines import OmniComposeAgentEngine, OmniLatentMASEngine, OmniAutoGPTEngine, OmniBabyAGIEngine
        from engines.omni_tool_engines import OmniLangcornEngine, OmniFacToolEngine, OmniSynalinksEngine, OmniMarkLLMEngine, OmniDataPrepEngine, OmniCalflopsEngine
        from engines.omni_rag_engines import OmniKGRAGEngine, OmniGenAITimelineEngine, OmniStarryDivineEngine, OmniLLMInterviewEngine, OmniAIBootcampEngine, OmniMindNLPEngine
        from engines.omni_audio_engines import OmniWhisperEngine, OmniBarkEngine, OmniMusicGenEngine
        from engines.omni_tuning_engines import OmniOmniQuantEngine, OmniLLMFinetuneEngine, OmniLoRATuneEngine, OmniDeepSpeedEngine, OmniRayServeEngine, OmniVLLMServeEngine

        engines = [
            OmniChatUniViEngine(), OmniMedicalMultimodalEngine(), OmniEagleEngine(), OmniStableDiffEngine(), OmniControlNetEngine(),
            OmniComposeAgentEngine(), OmniLatentMASEngine(), OmniAutoGPTEngine(), OmniBabyAGIEngine(),
            OmniLangcornEngine(), OmniFacToolEngine(), OmniSynalinksEngine(), OmniMarkLLMEngine(), OmniDataPrepEngine(), OmniCalflopsEngine(),
            OmniKGRAGEngine(), OmniGenAITimelineEngine(), OmniStarryDivineEngine(), OmniLLMInterviewEngine(), OmniAIBootcampEngine(), OmniMindNLPEngine(),
            OmniWhisperEngine(), OmniBarkEngine(), OmniMusicGenEngine(),
            OmniOmniQuantEngine(), OmniLLMFinetuneEngine(), OmniLoRATuneEngine(), OmniDeepSpeedEngine(), OmniRayServeEngine(), OmniVLLMServeEngine()
        ]
        
        for e in engines:
            h = e.health_check()
            self.assertEqual(h["status"], "healthy")
            self.assertTrue(h["engine_id"].endswith("-s14b10"))

if __name__ == "__main__":
    print("=" * 70)
    print("OMNI SEMESTER 14 BATCH 10 — INTEGRATION TEST SUITE")
    print("=" * 70)
    results = {"pass": 0, "fail": 0}
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBatch10Engines)
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
