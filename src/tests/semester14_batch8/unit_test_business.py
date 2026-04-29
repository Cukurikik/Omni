# Unit Tests — Business Layer (Python-only engines)
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_engine_registry():
    from engines.engine_registry import BATCH_8_ENGINE_REGISTRY, TOTAL_ENGINES
    assert TOTAL_ENGINES == 19, f"Expected 19 engines, got {TOTAL_ENGINES}"
    print(f"[PASS] Engine registry contains {TOTAL_ENGINES} engines")

def test_all_engines_health():
    from engines.omni_knowlm_engine import OmniKnowLMEngine
    from engines.omni_spacy_llm_engine import OmniSpacyLLMEngine
    from engines.omni_fastedit_engine import OmniFastEditEngine
    from engines.omni_bert4torch_engine import OmniBert4TorchEngine
    from engines.omni_dust_engine import OmniDustEngine
    from engines.omni_nlux_engine import OmniNLUXEngine
    from engines.omni_multi_engines import OmniSPINEngine, OmniTangoEngine, OmniParallaxEngine, OmniXLLMEngine
    from engines.omni_domain_engines import OmniMOSSTTSDEngine, OmniDriveLMEngine, OmniLLMAdaptersEngine
    from engines.omni_survey_engines import OmniText2SQLEngine, OmniRAGEngine, OmniAwesomeCodeLLMEngine

    engines = [OmniKnowLMEngine(), OmniSpacyLLMEngine(), OmniFastEditEngine(), OmniBert4TorchEngine(),
               OmniDustEngine(), OmniNLUXEngine(), OmniSPINEngine(), OmniTangoEngine(), OmniParallaxEngine(),
               OmniXLLMEngine(), OmniMOSSTTSDEngine(), OmniDriveLMEngine(), OmniLLMAdaptersEngine(),
               OmniText2SQLEngine(), OmniRAGEngine(), OmniAwesomeCodeLLMEngine()]
    for eng in engines:
        res = eng.health_check()
        assert res.is_ok, f"{eng.ENGINE_ID} health check failed"
    print(f"[PASS] All {len(engines)} engines passed health check")

if __name__ == "__main__":
    test_engine_registry()
    test_all_engines_health()
    print("ALL BUSINESS UNIT TESTS PASS")
