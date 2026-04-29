# Omni Mistral-Haystack RAG Builder (Python)
# Ref: anakin87/mistral-haystack
from typing import List, Dict

def build_rag_pipeline(retriever_type: str = "bm25", top_k: int = 5) -> Dict:
    return {"retriever": retriever_type, "top_k": top_k,
            "reader": "mistral-7b-instruct", "status": "ready"}

def format_context(documents: List[Dict]) -> str:
    return "\n\n".join(f"[{d.get('score', 0):.3f}] {d.get('content', '')}" for d in documents[:10])

def rag_generate(query: str, context: str) -> str:
    return f"Based on the following context:\n{context}\n\nAnswer: [response to: {query[:80]}]"
