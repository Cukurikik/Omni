"""OmniNomicEmbedVisionEngine.

Handles multimodal joint embedding scaling factors for
unified vision-text representation models like Nomic Embed.
"""
import sys
import os
import math
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniNomicEmbedVisionEngine:
    """Production engine for Nomic Vision embedding projections."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniNomicEmbedVisionEngine",
            "version": "1.0.0",
            "primitive": "vision_text_joint_embedding",
            "monadic_enforcement": True,
        }

    @staticmethod
    def normalize_l2(vector: List[float]) -> Result:
        """
        Strict L2 normalization for joint embedding spaces.
        """
        if not vector:
            return Err(ValueError("Empty vector"))
            
        magnitude_sq = sum(x*x for x in vector)
        if magnitude_sq == 0:
            return Err(ValueError("Zero vector cannot be normalized"))
            
        magnitude = math.sqrt(magnitude_sq)
        normalized = [x / magnitude for x in vector]
        
        return Ok(normalized)

    @staticmethod
    def check_modality_gap(text_emb: List[float], image_emb: List[float]) -> Result:
        """
        Computes the cosine distance modality gap between text and image
        embeddings.
        """
        if len(text_emb) != len(image_emb):
            return Err(ValueError("Dimension mismatch between text and image embeddings"))
            
        text_res = OmniNomicEmbedVisionEngine.normalize_l2(text_emb)
        image_res = OmniNomicEmbedVisionEngine.normalize_l2(image_emb)
        
        if text_res.is_err(): return text_res
        if image_res.is_err(): return image_res
        
        norm_t = text_res.unwrap()
        norm_i = image_res.unwrap()
        
        cosine_sim = sum(t * i for t, i in zip(norm_t, norm_i))
        modality_gap = 1.0 - cosine_sim
        
        return Ok({
            "cosine_similarity": cosine_sim,
            "modality_gap_distance": modality_gap,
            "aligned": modality_gap < 0.2
        })
