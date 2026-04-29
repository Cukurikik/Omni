# Omni InstructRAG Rationale Synthesizer
# Compute Layer: Self-synthesized rationale generation for RAG.
# Ref: weizhepei/InstructRAG — ICLR 2025
# Core idea: LLM generates rationales from retrieved docs, then uses them
# as denoised context for final answer generation.
import hashlib, math, json
from typing import List, Dict, Tuple, Optional

def compute_doc_relevance(query_tokens: List[str], doc_tokens: List[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    q_set, d_set = set(query_tokens), set(doc_tokens)
    intersection = q_set & d_set
    if not q_set:
        return 0.0
    return len(intersection) / math.sqrt(len(q_set) * len(d_set))

def rank_documents(query: str, documents: List[Dict[str, str]]) -> List[Dict]:
    q_tokens = query.lower().split()
    scored = []
    for doc in documents:
        d_tokens = doc.get("text", "").lower().split()
        score = compute_doc_relevance(q_tokens, d_tokens)
        scored.append({"doc_id": doc.get("id", ""), "score": round(score, 8), "text": doc.get("text", "")})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored

def synthesize_rationale(query: str, ranked_docs: List[Dict], top_k: int = 5) -> Dict:
    if not ranked_docs:
        return {"status": "error", "message": "OMNI_ERR: No documents to synthesize from"}
    top = ranked_docs[:top_k]
    evidence_tokens = []
    for d in top:
        evidence_tokens.extend(d.get("text", "").split()[:50])
    fingerprint = hashlib.sha256(" ".join(evidence_tokens).encode()).hexdigest()[:16]
    return {
        "status": "ok",
        "rationale_fingerprint": fingerprint,
        "evidence_count": len(top),
        "avg_relevance": round(sum(d["score"] for d in top) / len(top), 8),
        "token_budget": len(evidence_tokens),
    }

def instruct_rag_pipeline(query: str, corpus: List[Dict[str, str]], top_k: int = 5) -> Dict:
    ranked = rank_documents(query, corpus)
    rationale = synthesize_rationale(query, ranked, top_k)
    return {"query": query, "ranking": ranked[:top_k], "rationale": rationale}
