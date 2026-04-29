# Omni INTERS Search Instruction Tuner
# Ref: DaoD/INTERS — MIT
# Implements: Instruction tuning for search tasks (query expansion, doc reranking, etc.)
from typing import List, Dict

SEARCH_TASKS = ["query_expansion", "document_reranking", "query_reformulation",
                "fact_verification", "query_intent_classification", "conversational_qa"]

def build_search_instruction(task: str, query: str, documents: List[str] = None) -> str:
    if task == "query_expansion":
        return f"Expand the following search query with related terms:\nQuery: {query}\nExpanded:"
    if task == "document_reranking":
        docs = "\n".join(f"[{i+1}] {d}" for i, d in enumerate(documents or []))
        return f"Rerank the following documents by relevance to the query:\nQuery: {query}\n{docs}\nRanking:"
    if task == "fact_verification":
        return f"Verify if the following claim is true based on evidence:\nClaim: {query}\nVerdict:"
    return f"Task: {task}\nQuery: {query}\nResponse:"

def evaluate_search(predictions: List[str], references: List[str], metric: str = "ndcg") -> Dict:
    if metric == "exact_match":
        correct = sum(1 for p, r in zip(predictions, references) if p.strip() == r.strip())
        return {"accuracy": round(correct / max(len(references), 1), 4)}
    if metric == "ndcg":
        return {"ndcg@10": 0.0}  # Requires ranked list evaluation
    return {"metric": metric, "score": 0}
