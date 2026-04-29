"""
OMNI PrivateGPT RAG Engine
Local TF-IDF representation and exact cosine similarity metric.
"""
import math
from typing import Dict, Any, List
from collections import Counter
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniPrivateGPTRAGEngine(OmniBaseEngine):
    def __init__(self):
        super().__init__()

    def process(self, query: str, documents: List[str]) -> Result[List[float], str]:
        if not query or not documents:
            return Err("Query and document array must be populated.")
            
        try:
            def compute_tf(text: str) -> Dict[str, float]:
                words = text.lower().split()
                if not words:
                    return {}
                count = Counter(words)
                total = len(words)
                return {word: c / total for word, c in count.items()}
                
            q_tf = compute_tf(query)
            d_tfs = [compute_tf(doc) for doc in documents]
            
            all_words = set(q_tf.keys())
            for d in d_tfs:
                all_words.update(d.keys())
                
            idf = {}
            doc_count = len(documents)
            for word in all_words:
                containing_docs = sum(1 for d in d_tfs if word in d)
                idf[word] = math.log10((doc_count + 1) / (containing_docs + 1))
                
            def compute_vector(tf: Dict[str, float]) -> Dict[str, float]:
                return {word: tf.get(word, 0) * idf[word] for word in all_words}
                
            def cosine_sim(v1: Dict[str, float], v2: Dict[str, float]) -> float:
                dot = sum(v1[w] * v2[w] for w in all_words)
                mag1 = math.sqrt(sum(v ** 2 for v in v1.values()))
                mag2 = math.sqrt(sum(v ** 2 for v in v2.values()))
                if mag1 == 0 or mag2 == 0:
                    return 0.0
                return dot / (mag1 * mag2)
                
            q_vec = compute_vector(q_tf)
            similarities = []
            for d_tf in d_tfs:
                d_vec = compute_vector(d_tf)
                sim = cosine_sim(q_vec, d_vec)
                similarities.append(float(sim))
                
            return Ok(similarities)
        except Exception as e:
            return Err(f"Private RAG retrieval failed: {str(e)}")

    def diagnostics(self) -> Result[Dict[str, Any], str]:
        q = "artificial intelligence"
        docs = ["machine learning and artificial intelligence", "data science and statistics"]
        res = self.process(q, docs)
        if hasattr(res, 'is_ok') and res.is_ok():
            return Ok({"status": "healthy", "engine": "PrivateGPT TF-IDF RAG"})
        return Err("Diagnostics failed on PrivateGPT RAG engine.")
