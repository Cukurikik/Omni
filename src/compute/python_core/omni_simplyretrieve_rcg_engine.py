# Omni SimplyRetrieve RCG Engine
# Ref: RCGAI/SimplyRetrieve — MIT
# Implements: Retrieval-Centric Generation with strict retriever/LLM separation
import math
from typing import List, Dict, Tuple

def build_knowledge_base(documents: List[Dict]) -> Dict:
    index = {}
    for doc in documents:
        tokens = doc.get("text", "").lower().split()
        doc_id = doc.get("id", str(id(doc)))
        for token in set(tokens):
            index.setdefault(token, []).append(doc_id)
    return {"index": index, "n_docs": len(documents), "vocab_size": len(index)}

def rcg_retrieve(query: str, index: Dict, documents: List[Dict], top_k: int = 5) -> List[Dict]:
    q_tokens = set(query.lower().split())
    scores = {}
    for token in q_tokens:
        for doc_id in index.get("index", {}).get(token, []):
            scores[doc_id] = scores.get(doc_id, 0) + 1
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    doc_map = {d.get("id", str(i)): d for i, d in enumerate(documents)}
    return [{"id": did, "score": round(s / max(len(q_tokens), 1), 4), "text": doc_map.get(did, {}).get("text", "")} for did, s in ranked]

def retrieval_tuning_score(retrieved: List[Dict], relevant_ids: set) -> Dict:
    hits = sum(1 for r in retrieved if r["id"] in relevant_ids)
    precision = hits / max(len(retrieved), 1)
    recall = hits / max(len(relevant_ids), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
