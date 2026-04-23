"""OmniDocrunnerCodeblockValidatorEngine — Markdown Code Block Extraction & Validation.

Inspired by srinivasayush/docrunner: a CLI tool that extracts code
blocks from markdown files and runs them to ensure documentation
examples are always up-to-date and functional.

Algorithmic Primitive:
    Parse a markdown document, extract fenced code blocks with their
    language tags, validate that required languages are present,
    detect duplicate code blocks, and compute a coverage score
    (ratio of validated blocks to total blocks).
"""
from __future__ import annotations
import re
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniDocrunnerCodeblockValidatorEngine:
    """Production-grade markdown code block extractor and validator."""

    # Regex for fenced code blocks: ```language\n...code...\n```
    FENCE_PATTERN = re.compile(
        r'^```(\w*)\s*\n(.*?)^```',
        re.MULTILINE | re.DOTALL,
    )

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniDocrunnerCodeblockValidatorEngine",
            "version": "1.0.0",
            "primitive": "markdown_fenced_codeblock_extraction_validation",
            "monadic_enforcement": True,
            "source_repo": "srinivasayush/docrunner",
        }

    @staticmethod
    def extract_code_blocks(markdown: str) -> Result:
        """Extract all fenced code blocks from a markdown string.

        Args:
            markdown: The raw markdown content.

        Returns:
            Result[list[dict], Exception]: List of dicts, each with
            'language' (str) and 'code' (str).
        """
        if not isinstance(markdown, str):
            return Err(Exception("markdown must be a string"))
        if not markdown.strip():
            return Err(Exception("markdown content is empty"))

        blocks: list[dict] = []
        for match in OmniDocrunnerCodeblockValidatorEngine.FENCE_PATTERN.finditer(markdown):
            lang = match.group(1) or "unknown"
            code = match.group(2).strip()
            blocks.append({"language": lang, "code": code})

        return Ok(blocks)

    @staticmethod
    def validate_required_languages(
        blocks: list[dict],
        required_languages: list[str],
    ) -> Result:
        """Validate that code blocks for all required languages exist.

        Args:
            blocks: List of extracted code blocks (language, code).
            required_languages: List of required language identifiers.

        Returns:
            Result[dict, Exception]: dict with 'valid', 'missing_languages',
            'found_languages'.
        """
        if not isinstance(blocks, list):
            return Err(Exception("blocks must be a list"))
        if not isinstance(required_languages, list):
            return Err(Exception("required_languages must be a list"))

        found = {b["language"] for b in blocks if isinstance(b, dict) and "language" in b}
        missing = [lang for lang in required_languages if lang not in found]

        return Ok({
            "valid": len(missing) == 0,
            "missing_languages": missing,
            "found_languages": sorted(found),
        })

    @staticmethod
    def compute_coverage(
        total_blocks: int,
        validated_blocks: int,
    ) -> Result:
        """Compute documentation code coverage score.

        Args:
            total_blocks: Total number of code blocks in documentation.
            validated_blocks: Number of blocks that passed validation.

        Returns:
            Result[dict, Exception]: dict with 'coverage' (0.0 to 1.0),
            'total', 'validated', 'unvalidated'.
        """
        if total_blocks < 0 or validated_blocks < 0:
            return Err(Exception("Block counts must be non-negative"))
        if validated_blocks > total_blocks:
            return Err(Exception("validated_blocks cannot exceed total_blocks"))
        if total_blocks == 0:
            return Ok({
                "coverage": 1.0,
                "total": 0,
                "validated": 0,
                "unvalidated": 0,
            })

        coverage = round(validated_blocks / total_blocks, 6)
        return Ok({
            "coverage": coverage,
            "total": total_blocks,
            "validated": validated_blocks,
            "unvalidated": total_blocks - validated_blocks,
        })

    @staticmethod
    def detect_duplicates(blocks: list[dict]) -> Result:
        """Detect duplicate code blocks by content hash.

        Args:
            blocks: List of code block dicts with 'code' field.

        Returns:
            Result[list[list[int]], Exception]: List of duplicate groups
            (each group is a list of block indices with identical code).
        """
        if not isinstance(blocks, list):
            return Err(Exception("blocks must be a list"))

        code_to_indices: dict[str, list[int]] = {}
        for i, block in enumerate(blocks):
            code = block.get("code", "")
            if code in code_to_indices:
                code_to_indices[code].append(i)
            else:
                code_to_indices[code] = [i]

        duplicates = [indices for indices in code_to_indices.values() if len(indices) > 1]

        return Ok(duplicates)
