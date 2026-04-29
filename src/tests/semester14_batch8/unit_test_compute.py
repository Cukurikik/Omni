# Unit Tests — KnowLM KV Cache Compute
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from compute.knowlm_trainer import KnowLMTrainer, OmniResult

def test_omni_result():
    r = OmniResult(value=42)
    assert r.is_ok and r.value == 42
    r = OmniResult(error="fail")
    assert not r.is_ok and r.error == "fail"
    print("[PASS] OmniResult monadic behavior verified")

def test_compute_imports():
    from compute.spin_selfplay_loss import SPINLoss
    from compute.tango_clap_scorer import CLAPScorer
    from compute.bert4torch_builder import Bert4TorchBuilder
    from compute.drivelm_pipeline import DriveLMPipeline
    from compute.moss_ttsd_voice_cloner import VoiceCloner
    from compute.spacy_llm_extractor import SpacyLLMExtractor
    print("[PASS] All compute modules importable")

if __name__ == "__main__":
    test_omni_result()
    test_compute_imports()
    print("ALL UNIT TESTS PASS")
