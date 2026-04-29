# Semester 14 Batch 8 — Full Integration Test Suite
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestResult:
    def __init__(self): self.passed = 0; self.failed = 0; self.errors = []
    def ok(self, name): self.passed += 1; print(f"  [PASS] {name}")
    def fail(self, name, reason): self.failed += 1; self.errors.append(f"{name}: {reason}"); print(f"  [FAIL] {name}: {reason}")

def run_all():
    r = TestResult()
    print("=" * 70)
    print("OMNI SEMESTER 14 BATCH 8 — INTEGRATION TEST SUITE")
    print("=" * 70)

    # === ENGINE HEALTH CHECKS ===
    print("\n[ENGINE HEALTH CHECKS]")
    from engines.omni_knowlm_engine import OmniKnowLMEngine
    from engines.omni_spacy_llm_engine import OmniSpacyLLMEngine
    from engines.omni_fastedit_engine import OmniFastEditEngine
    from engines.omni_bert4torch_engine import OmniBert4TorchEngine
    from engines.omni_dust_engine import OmniDustEngine
    from engines.omni_nlux_engine import OmniNLUXEngine
    from engines.omni_multi_engines import OmniSPINEngine, OmniTangoEngine, OmniParallaxEngine, OmniXLLMEngine
    from engines.omni_domain_engines import OmniMOSSTTSDEngine, OmniDriveLMEngine, OmniLLMAdaptersEngine
    from engines.omni_survey_engines import OmniText2SQLEngine, OmniRAGEngine, OmniAwesomeCodeLLMEngine, OmniEfficientLLMEngine, OmniMultiAgentEngine, OmniKEPapersEngine

    engines = [OmniKnowLMEngine(), OmniSpacyLLMEngine(), OmniFastEditEngine(), OmniBert4TorchEngine(),
               OmniDustEngine(), OmniNLUXEngine(), OmniSPINEngine(), OmniTangoEngine(), OmniParallaxEngine(),
               OmniXLLMEngine(), OmniMOSSTTSDEngine(), OmniDriveLMEngine(), OmniLLMAdaptersEngine(),
               OmniText2SQLEngine(), OmniRAGEngine(), OmniAwesomeCodeLLMEngine(), OmniEfficientLLMEngine(),
               OmniMultiAgentEngine(), OmniKEPapersEngine()]
    for eng in engines:
        res = eng.health_check()
        name = eng.ENGINE_ID
        if res.is_ok and res.value.get("status") == "operational":
            r.ok(name)
        else:
            r.fail(name, str(res.error))

    # === COMPUTE LAYER TESTS ===
    print("\n[COMPUTE LAYER TESTS]")
    from compute.bert4torch_builder import Bert4TorchBuilder
    b = Bert4TorchBuilder()
    res = b.build_config(12, 768, 12, 30522)
    if res.is_ok: r.ok("bert4torch_builder_valid")
    else: r.fail("bert4torch_builder_valid", res.error)
    res = b.build_config(999, 768, 12, 30522)
    if not res.is_ok: r.ok("bert4torch_builder_reject_layers")
    else: r.fail("bert4torch_builder_reject_layers", "Should reject")
    res = b.build_config(12, 768, 7, 30522)
    if not res.is_ok: r.ok("bert4torch_builder_reject_indivisible")
    else: r.fail("bert4torch_builder_reject_indivisible", "Should reject")

    from compute.spin_selfplay_loss import SPINLoss
    try:
        loss = SPINLoss(0.1); r.ok("spin_loss_init_valid")
    except: r.fail("spin_loss_init_valid", "Init failed")
    try:
        loss = SPINLoss(-1); r.fail("spin_loss_reject_negative", "Should raise")
    except ValueError: r.ok("spin_loss_reject_negative")

    from compute.spacy_llm_extractor import SpacyLLMExtractor
    ext = SpacyLLMExtractor()
    res = ext.extract_entities("Hello world", ["PERSON"])
    if res.is_ok: r.ok("spacy_llm_extract_valid")
    else: r.fail("spacy_llm_extract_valid", res.error)
    res = ext.extract_entities("x" * 200000, ["PERSON"])
    if not res.is_ok: r.ok("spacy_llm_reject_long_text")
    else: r.fail("spacy_llm_reject_long_text", "Should reject")

    # === REGISTRY TEST ===
    print("\n[REGISTRY TEST]")
    from engines.engine_registry import BATCH_8_ENGINE_REGISTRY, TOTAL_ENGINES
    if TOTAL_ENGINES == 19: r.ok("registry_count_19")
    else: r.fail("registry_count_19", f"Got {TOTAL_ENGINES}")

    # === SUMMARY ===
    print("\n" + "=" * 70)
    total = r.passed + r.failed
    print(f"TOTAL: {total} | PASSED: {r.passed} | FAILED: {r.failed}")
    if r.errors:
        print("ERRORS:")
        for e in r.errors: print(f"  - {e}")
    status = "ALL PASS" if r.failed == 0 else "FAILURES DETECTED"
    print(f"STATUS: {status}")
    print("=" * 70)
    return r.failed == 0

if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
