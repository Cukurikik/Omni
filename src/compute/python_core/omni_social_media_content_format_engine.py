"""OmniSocialMediaContentFormatEngine — XHS Post Structuring & Hashtags.

Inspired by ALYAHWI/xhs-ai-writer: an AI-powered tool designed for
crafting engaging posts that resonate with readers on platforms
like XiaoHongShu (XHS).

Algorithmic Primitive:
    Analyze text to automatically extract implicit hashtags based on
    word frequency or explicit formatting, and compile raw content
    into a strictly structured social media post format optimized
    for timeline engagement.
"""
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from __future__ import annotations
import re
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniSocialMediaContentFormatEngine:
    """Production-grade social media formatting and hashtag extraction engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniSocialMediaContentFormatEngine",
            "version": "1.0.0",
            "primitive": "social_media_structure_hashtag_extraction",
            "monadic_enforcement": True,
            "source_repo": "ALYAHWI/xhs-ai-writer",
        }

    @staticmethod
    def extract_hashtags_from_text(text: str) -> Result:
        """Extract explicit hashtags from text content.

        Args:
            text: The raw text that may contain `#hashtag` expressions.

        Returns:
            Result[list[str], Exception]: A deduplicated, lowercased list of hashtags.
        """
        if not isinstance(text, str):
            return Err(Exception("text must be a string"))

        pattern = re.compile(r'#(\w+)')
        tags = pattern.findall(text)
        deduped = list(dict.fromkeys([t.lower() for t in tags]))
        return Ok(deduped)

    @staticmethod
    def format_post(
        title: str,
        body_sections: list[str],
        base_hashtags: list[str],
        auto_extract: bool = True,
    ) -> Result:
        """Format social media post with emojis, spacing, and unified tags.

        Args:
            title: The attention-grabbing title.
            body_sections: List of paragraphs for the post body.
            base_hashtags: List of predefined tags.
            auto_extract: If True, extract hashtags from body implicitly.

        Returns:
            Result[str, Exception]: Formatted multi-line post string.
        """
        if not isinstance(title, str) or not isinstance(body_sections, list) or not isinstance(base_hashtags, list):
            return Err(Exception("Invalid data types for format_post arguments"))

        unified_tags: set[str] = set([t.replace("#", "").lower() for t in base_hashtags])

        formatted_body_parts = []
        for i, section in enumerate(body_sections):
            if not isinstance(section, str):
                return Err(Exception(f"Body section at index {i} is not a string"))
                
            clean_sec = section.strip()
            if not clean_sec:
                continue

            if auto_extract:
                extracted_res = OmniSocialMediaContentFormatEngine.extract_hashtags_from_text(clean_sec)
                if extracted_res.is_ok():
                    unified_tags.update(extracted_res.unwrap())
            
            # Remove inline hashtags from body presentation to stack them at the bottom
            clean_sec = re.sub(r'#(\w+)', '', clean_sec).strip()
            if clean_sec:
                formatted_body_parts.append(clean_sec)

        # Assemble
        lines = []
        
        # Title with XHS-style emoji decorators
        clean_title = title.strip()
        lines.append(f"✨ {clean_title} ✨")
        lines.append("")
        
        # Body
        for part in formatted_body_parts:
            lines.append(f"👉 {part}")
            lines.append("")
            
        # Tags
        if unified_tags:
            lines.append(" ".join(f"#{tag}" for tag in sorted(unified_tags)))

        return Ok("\n".join(lines).strip())
