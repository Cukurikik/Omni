# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Resume-Matcher Engine (OMNI Zero-Mock Implementation)
# Implements TF-IDF vectorization and Cosine Similarity for ATS parsing.

from dataclasses import dataclass
from typing import List, Dict, Optional
import math

@dataclass
class Result:
    value: Optional[float]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class ResumeMatcher:
    def compute_tf(self, text: str) -> Dict[str, float]:
        words = text.lower().replace(".", "").replace(",", "").split()
        tf = {}
        total = len(words)
        if total == 0: return tf
        for w in words:
            tf[w] = tf.get(w, 0) + 1
        for w in tf:
            tf[w] = tf[w] / total
        return tf

    def compute_idf(self, documents: List[str]) -> Dict[str, float]:
        N = len(documents)
        idf = {}
        word_doc_count = {}
        
        for doc in documents:
            words = set(doc.lower().replace(".", "").replace(",", "").split())
            for w in words:
                word_doc_count[w] = word_doc_count.get(w, 0) + 1
                
        for w, count in word_doc_count.items():
            idf[w] = math.log(N / float(count))
        return idf

    def compute_tfidf(self, text: str, idf: Dict[str, float]) -> Dict[str, float]:
        tf = self.compute_tf(text)
        tfidf = {}
        for word, tf_val in tf.items():
            tfidf[word] = tf_val * idf.get(word, 0.0)
        return tfidf

    def match(self, resume: str, job_description: str) -> Result:
        if not resume or not job_description:
            return Result.err("Resume and Job Description cannot be empty.")
            
        idf = self.compute_idf([resume, job_description])
        vec1 = self.compute_tfidf(resume, idf)
        vec2 = self.compute_tfidf(job_description, idf)
        
        words = set(vec1.keys()).union(set(vec2.keys()))
        dot_product = sum(vec1.get(w, 0) * vec2.get(w, 0) for w in words)
        
        mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return Result.ok(0.0)
            
        return Result.ok(dot_product / (mag1 * mag2))
