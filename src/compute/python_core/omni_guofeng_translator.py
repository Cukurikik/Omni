# Omni GuoFeng Webnovel Translation Engine
# Ref: longyuewangdcu/GuoFeng-Webnovel
from typing import List, Dict

def segment_novel(text: str, max_tokens: int = 512) -> List[str]:
    sentences = text.replace("。", "。\n").replace(". ", ".\n").split("\n")
    segments, current = [], ""
    for s in sentences:
        if len(current.split()) + len(s.split()) > max_tokens:
            if current: segments.append(current.strip())
            current = s
        else:
            current += " " + s
    if current: segments.append(current.strip())
    return segments

def literary_quality_score(translation: str) -> Dict:
    words = translation.split()
    unique = len(set(w.lower() for w in words))
    diversity = unique / max(len(words), 1)
    avg_len = sum(len(w) for w in words) / max(len(words), 1)
    return {"lexical_diversity": round(diversity, 4), "avg_word_length": round(avg_len, 2),
            "fluency_estimate": round(min(diversity * 1.5, 1.0), 4)}

def align_bilingual_segments(src: List[str], tgt: List[str]) -> List[Dict]:
    return [{"src": s, "tgt": t, "length_ratio": round(len(t.split())/max(len(s.split()),1), 2)}
            for s, t in zip(src, tgt)]
