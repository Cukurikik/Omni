# Omni BlossomLM Training Data Engine
# Ref: Azure99/BlossomLM — Apache-2.0
from typing import List, Dict
import hashlib

def quality_filter(samples: List[Dict], min_len: int = 20, max_len: int = 4096) -> List[Dict]:
    return [s for s in samples if min_len <= len(s.get("text","").split()) <= max_len]

def dedup_hash(samples: List[Dict]) -> List[Dict]:
    seen = set(); result = []
    for s in samples:
        h = hashlib.md5(s.get("text","").encode()).hexdigest()
        if h not in seen: seen.add(h); result.append(s)
    return result

def sft_format(instruction: str, input_text: str, output: str) -> Dict:
    return {"conversations": [{"role":"user","content": f"{instruction}\n{input_text}".strip()}, {"role":"assistant","content": output}]}

def dataset_stats(samples: List[Dict]) -> Dict:
    lengths = [len(s.get("text","").split()) for s in samples]
    return {"n_samples": len(samples), "avg_len": round(sum(lengths)/max(len(lengths),1),1), "max_len": max(lengths) if lengths else 0}
