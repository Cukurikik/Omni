# Omni Loong Multi-Doc QA Engine (Python)
# Compute Layer: Extended multi-document QA with long-context LLMs.
# Ref: MozerWang/Loong — EMNLP 2024 Oral, Leave No Document Behind.

from typing import List, Dict, Tuple

class Document:
    __slots__ = ('doc_id', 'content', 'relevance_score')
    def __init__(self, doc_id: str, content: str, relevance_score: float = 0.0):
        self.doc_id = doc_id
        self.content = content
        self.relevance_score = max(0.0, min(1.0, relevance_score))

def rank_documents(docs: List[Document]) -> List[Document]:
    return sorted(docs, key=lambda d: d.relevance_score, reverse=True)

def compute_context_window(docs: List[Document], max_tokens: int) -> List[Document]:
    selected: List[Document] = []
    total = 0
    for d in rank_documents(docs):
        tokens = len(d.content.split())
        if total + tokens > max_tokens: break
        selected.append(d)
        total += tokens
    return selected

def evaluate_qa_accuracy(predictions: List[str], gold: List[str]) -> float:
    if not gold: return 0.0
    correct = sum(1 for p, g in zip(predictions, gold) if p.strip().lower() == g.strip().lower())
    return round(correct / len(gold), 6)
