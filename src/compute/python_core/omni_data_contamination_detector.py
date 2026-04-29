# Omni Data Contamination Detector
# Ref: lyy1994/awesome-data-contamination — MIT
from typing import List, Dict
import hashlib

def ngram_overlap(train_text: str, test_text: str, n: int = 8) -> float:
    t1 = train_text.split(); t2 = test_text.split()
    ng1 = set(tuple(t1[i:i+n]) for i in range(len(t1)-n+1))
    ng2 = set(tuple(t2[i:i+n]) for i in range(len(t2)-n+1))
    if not ng2: return 0.0
    return round(len(ng1 & ng2) / len(ng2), 6)

def fingerprint_match(text: str, known_hashes: set) -> bool:
    h = hashlib.sha256(text.strip().encode()).hexdigest()[:16]
    return h in known_hashes

def contamination_report(test_samples: List[str], train_corpus: str, n: int = 8) -> Dict:
    flagged = sum(1 for s in test_samples if ngram_overlap(train_corpus, s, n) > 0.3)
    return {"total": len(test_samples), "flagged": flagged,
            "rate": round(flagged / max(len(test_samples), 1), 4)}
