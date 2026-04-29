# Omni Advanced RAG Pipeline
# Ref: GURPREETKAURJETHRA/Advanced_RAG
# Implements: Corrective RAG, Self-RAG, Agentic RAG patterns
from typing import List, Dict

def corrective_rag(query: str, retrieved_docs: List[Dict], relevance_threshold: float = 0.5) -> Dict:
    relevant = [d for d in retrieved_docs if d.get("score", 0) >= relevance_threshold]
    if not relevant:
        return {"action": "web_search", "reason": "no_relevant_docs", "docs": []}
    return {"action": "generate", "reason": "docs_sufficient", "docs": relevant}

def self_rag_evaluate(response: str, context: str) -> Dict:
    r_tokens = set(response.lower().split()); c_tokens = set(context.lower().split())
    support = len(r_tokens & c_tokens) / max(len(r_tokens), 1)
    return {"is_supported": support > 0.3, "support_score": round(support, 4),
            "action": "accept" if support > 0.3 else "regenerate"}

def reciprocal_rank_fusion(ranked_lists: List[List[str]], k: int = 60) -> List[str]:
    scores: Dict[str, float] = {}
    for rl in ranked_lists:
        for rank, doc_id in enumerate(rl):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (rank + k)
    return sorted(scores.keys(), key=lambda d: scores[d], reverse=True)

def adaptive_chunk(text: str, min_size: int = 200, max_size: int = 500) -> List[str]:
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) > max_size and len(current) >= min_size:
            chunks.append(current.strip()); current = s
        else: current += ". " + s if current else s
    if current: chunks.append(current.strip())
    return chunks
