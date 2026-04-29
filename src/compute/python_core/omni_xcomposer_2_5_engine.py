"""OmniXComposer25Engine.

Coordinates text-image interleaving and webpage rendering alignment
for InternLM-XComposer-2.5.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniXComposer25Engine:
    """Zero-mock engine for interleaved text-image coordinate alignment."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniXComposer25Engine",
            "version": "1.0.0",
            "primitive": "interleaved_coordinate_aligner",
            "monadic_enforcement": True,
        }

    @staticmethod
    def align_interleaved_document(blocks: List[Dict[str, Any]]) -> Result:
        """
        Validates the sequence of interleaved text and image blocks,
        ensuring proper formatting for XComposer ingestion.
        """
        if not blocks:
            return Err(ValueError("Blocks list is empty"))
            
        aligned_sequence = []
        image_count = 0
        text_count = 0
        
        for idx, block in enumerate(blocks):
            b_type = block.get("type")
            if b_type not in ["text", "image"]:
                return Err(ValueError(f"Invalid block type at index {idx}: {b_type}"))
                
            if b_type == "image":
                image_count += 1
                aligned_sequence.append(f"<Image-{image_count}>")
            elif b_type == "text":
                text_count += 1
                content = block.get("content", "")
                aligned_sequence.append(content)
                
        return Ok({
            "sequence_pattern": " ".join(aligned_sequence),
            "total_images": image_count,
            "total_text_blocks": text_count,
            "is_valid_interleaved": image_count > 0 and text_count > 0
        })
