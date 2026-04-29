# Omni Tool Retrieval Benchmark Engine
# Ref: mangopy/tool-retrieval-benchmark — Apache-2.0, ACL 2025
from typing import List, Dict

def build_tool_corpus(tools: List[Dict]) -> Dict:
    index = {}
    for tool in tools:
        tokens = set(tool.get("description", "").lower().split() + tool.get("name", "").lower().split())
        for t in tokens: index.setdefault(t, []).append(tool.get("name", ""))
    return {"index": index, "n_tools": len(tools)}

def retrieve_tools(query: str, corpus: Dict, top_k: int = 5) -> List[Dict]:
    q_tokens = query.lower().split()
    scores = {}
    for t in q_tokens:
        for name in corpus.get("index", {}).get(t, []):
            scores[name] = scores.get(name, 0) + 1
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{"tool": name, "score": round(s / max(len(q_tokens), 1), 4)} for name, s in ranked]

def tool_retrieval_metrics(retrieved: List[str], relevant: List[str], k: int = 5) -> Dict:
    hits = sum(1 for r in retrieved[:k] if r in relevant)
    recall = hits / max(len(relevant), 1)
    ndcg = sum(1 / math.log2(i + 2) for i, r in enumerate(retrieved[:k]) if r in relevant)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    import math
    return {"recall@k": round(recall, 4), "ndcg@k": round(ndcg / max(ideal, 1e-9), 4)}
