# Omni Magikarp Tokenizer Anomaly Detector
# Ref: cohere-ai/magikarp — Apache-2.0
from typing import List, Dict
import math
def detect_undertrained_tokens(vocab_logprobs: Dict[str,float], threshold_std: float = 3.0) -> List[str]:
    vals = list(vocab_logprobs.values())
    if not vals: return []
    mean = sum(vals)/len(vals); std = math.sqrt(sum((v-mean)**2 for v in vals)/len(vals)) or 1
    return [tok for tok, lp in vocab_logprobs.items() if lp < mean - threshold_std * std]
def token_frequency_analysis(token_counts: Dict[str,int]) -> Dict:
    total = sum(token_counts.values()) or 1
    sorted_t = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
    return {"total": total, "unique": len(token_counts),
            "top10": sorted_t[:10], "bottom10": sorted_t[-10:]}
def glitch_token_score(token: str, logprob: float, vocab_mean: float, vocab_std: float) -> float:
    return round(abs(logprob - vocab_mean) / max(vocab_std, 1e-6), 4)
