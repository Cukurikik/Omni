"""
omni_retriever_eval.py — Retrieval Evaluation Metrics
Layer: Domain / Python

Computes Mean Reciprocal Rank (MRR) and Normalized Discounted Cumulative Gain
(NDCG) to rigorously evaluate the accuracy of the Hybrid Search RAG retriever.
"""

import math
from typing import List, Dict

class OmniRetrievalEvaluator:
    """
    Evaluates search result rankings against ground-truth relevant documents.
    """
    
    @staticmethod
    def calculate_mrr(rankings: List[List[str]], ground_truths: List[List[str]]) -> float:
        """
        Mean Reciprocal Rank (MRR).
        rankings: List of document IDs returned by the search, per query.
        ground_truths: List of relevant document IDs per query.
        """
        assert len(rankings) == len(ground_truths)
        
        mrr_sum = 0.0
        for ranked_docs, true_docs in zip(rankings, ground_truths):
            true_set = set(true_docs)
            reciprocal_rank = 0.0
            
            for i, doc_id in enumerate(ranked_docs):
                if doc_id in true_set:
                    reciprocal_rank = 1.0 / (i + 1)
                    break # Only care about the first relevant document for MRR
            
            mrr_sum += reciprocal_rank
            
        return mrr_sum / len(rankings) if rankings else 0.0

    @staticmethod
    def calculate_ndcg(rankings: List[List[str]], ground_truths: List[List[str]], k: int = 10) -> float:
        """
        Normalized Discounted Cumulative Gain (NDCG@K).
        """
        assert len(rankings) == len(ground_truths)
        
        ndcg_sum = 0.0
        for ranked_docs, true_docs in zip(rankings, ground_truths):
            true_set = set(true_docs)
            
            # Calculate DCG@K
            dcg = 0.0
            for i, doc_id in enumerate(ranked_docs[:k]):
                if doc_id in true_set:
                    dcg += 1.0 / math.log2(i + 2) # Relevance is binary (0 or 1) here
                    
            # Calculate IDCG@K (Ideal DCG)
            idcg = 0.0
            ideal_hits = min(len(true_set), k)
            for i in range(ideal_hits):
                idcg += 1.0 / math.log2(i + 2)
                
            if idcg > 0:
                ndcg_sum += (dcg / idcg)
                
        return ndcg_sum / len(rankings) if rankings else 0.0
