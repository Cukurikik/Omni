from typing import List, Dict, Tuple, Optional
import math

# OMNI bRAG-langchain: Agentic RAG Retrieval Graph
# Pure implementation of retrieval and re-ranking algorithms without heavy framework bloat.
# Source: bragai/bRAG-langchain

class Document:
    def __init__(self, id: str, content: str, embedding: List[float]):
        self.id = id
        self.content = content
        self.embedding = embedding

class RAGError(Exception):
    pass

class AgenticRetriever:
    """
    Implements vector similarity search and cross-attention re-ranking logic.
    """
    def __init__(self, knowledge_base: List[Document]):
        self.kb = knowledge_base

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if len(vec1) != len(vec2):
            raise ValueError("Vector dimensions must match")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def retrieve(self, query_embedding: List[float], top_k: int = 5) -> Tuple[Optional[List[Document]], Optional[RAGError]]:
        """
        Primary dense retrieval step.
        """
        try:
            scores = []
            for doc in self.kb:
                sim = self.cosine_similarity(query_embedding, doc.embedding)
                scores.append((sim, doc))
            
            # Sort by descending similarity
            scores.sort(key=lambda x: x[0], reverse=True)
            
            top_docs = [doc for score, doc in scores[:top_k]]
            return top_docs, None
            
        except Exception as e:
            return None, RAGError(f"Retrieval failed: {str(e)}")

    def rerank(self, query: str, docs: List[Document], llm_evaluator) -> Tuple[Optional[List[Document]], Optional[RAGError]]:
        """
        Agentic re-ranking: Uses an LLM or cross-encoder to score relevance strictly.
        """
        try:
            scored_docs = []
            for doc in docs:
                # llm_evaluator returns a score 0.0 to 1.0 based on query + doc
                score = llm_evaluator(query, doc.content)
                scored_docs.append((score, doc))
                
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            return [doc for score, doc in scored_docs if score > 0.5], None # Thresholding
            
        except Exception as e:
            return None, RAGError(f"Reranking failed: {str(e)}")

# Orchestrator
def run_agentic_rag(query_str: str, query_emb: List[float], retriever: AgenticRetriever, evaluator) -> Tuple[Optional[str], Optional[RAGError]]:
    docs, err = retriever.retrieve(query_emb, top_k=10)
    if err: return None, err
    
    refined_docs, err = retriever.rerank(query_str, docs, evaluator)
    if err: return None, err
    
    # Synthesize context
    context = "\n\n".join([d.content for d in refined_docs])
    return f"Context:\n{context}\n\nAnswer the query: {query_str}", None
