# Omni LMT Multilingual Translator
# Compute: Scalable high-performance multilingual translation model logic.
# Ref: NiuTrans/LMT — Multilingual MT
import hashlib, math
from typing import Dict, List

LANG_FAMILIES = {"zh":"sino-tibetan","ja":"japonic","ko":"koreanic","en":"germanic",
    "de":"germanic","fr":"romance","es":"romance","pt":"romance","ar":"semitic","hi":"indo-aryan","ru":"slavic"}

def detect_lang_family(lang_code: str) -> str:
    return LANG_FAMILIES.get(lang_code.lower(), "unknown")

def compute_bleu_precision(candidate: List[str], reference: List[str], n: int = 4) -> float:
    if not candidate: return 0.0
    scores = []
    for k in range(1, n + 1):
        c_ngrams = [tuple(candidate[i:i+k]) for i in range(len(candidate)-k+1)]
        r_ngrams = set(tuple(reference[i:i+k]) for i in range(len(reference)-k+1))
        if not c_ngrams: scores.append(0.0); continue
        matches = sum(1 for ng in c_ngrams if ng in r_ngrams)
        scores.append(matches / len(c_ngrams))
    if any(s == 0 for s in scores): return 0.0
    log_avg = sum(math.log(s) for s in scores) / len(scores)
    bp = min(1.0, math.exp(1 - len(reference) / max(len(candidate), 1)))
    return round(bp * math.exp(log_avg), 6)

def translation_quality(src: str, tgt: str, ref: str) -> Dict:
    bleu = compute_bleu_precision(tgt.split(), ref.split())
    return {"bleu": bleu, "src_len": len(src.split()), "tgt_len": len(tgt.split()), "ref_len": len(ref.split())}
