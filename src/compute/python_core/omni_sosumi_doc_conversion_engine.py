"""OmniSosumiDocConversionEngine — Structured Doc to Markdown Transformer.

Inspired by kanaa257/sosumi.ai: a TypeScript tool that converts Apple
Developer documentation from structured JSON data into clean,
AI-readable Markdown format with URL rewriting.

Algorithmic Primitive:
    Given a hierarchical documentation tree (sections with nested
    subsections, code blocks, and cross-references), flatten it into
    a well-formatted Markdown string. Rewrite internal URLs from
    one domain to another and compute a table-of-contents from
    heading structure.
"""
from __future__ import annotations
import re
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniSosumiDocConversionEngine:
    """Production-grade documentation format conversion engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniSosumiDocConversionEngine",
            "version": "1.0.0",
            "primitive": "hierarchical_doc_tree_markdown_flattening",
            "monadic_enforcement": True,
            "source_repo": "kanaa257/sosumi.ai",
        }

    @staticmethod
    def flatten_doc_tree(sections: list[dict], depth: int = 1) -> Result:
        """Flatten a hierarchical documentation tree to Markdown.

        Args:
            sections: List of section dicts, each with:
                - 'title': str — section heading
                - 'content': str — section body text
                - 'code': optional str — code block content
                - 'language': optional str — code language for fencing
                - 'children': optional list of sub-sections (same format)
            depth: Starting heading depth (1 = h1, 2 = h2, etc.)

        Returns:
            Result[str, Exception]: The complete Markdown string.
        """
        if not isinstance(sections, list):
            return Err(Exception("sections must be a list"))
        if depth < 1 or depth > 6:
            return Err(Exception("depth must be between 1 and 6"))

        lines: list[str] = []
        for section in sections:
            if not isinstance(section, dict):
                return Err(Exception("Each section must be a dict"))

            title = section.get("title", "")
            content = section.get("content", "")
            code = section.get("code")
            language = section.get("language", "")
            children = section.get("children", [])

            # Heading
            if title:
                lines.append(f"{'#' * min(depth, 6)} {title}")
                lines.append("")

            # Body text
            if content:
                lines.append(content)
                lines.append("")

            # Code block
            if code:
                lines.append(f"```{language}")
                lines.append(code)
                lines.append("```")
                lines.append("")

            # Recurse into children
            if children:
                child_result = OmniSosumiDocConversionEngine.flatten_doc_tree(
                    children, min(depth + 1, 6)
                )
                if not child_result.is_ok():
                    return child_result
                lines.append(child_result.unwrap())

        return Ok("\n".join(lines))

    @staticmethod
    def rewrite_urls(
        markdown: str,
        source_domain: str,
        target_domain: str,
    ) -> Result:
        """Rewrite all URLs from source domain to target domain.

        Args:
            markdown: The markdown text.
            source_domain: e.g. "developer.apple.com"
            target_domain: e.g. "sosumi.ai"

        Returns:
            Result[dict, Exception]: dict with 'markdown' (rewritten text),
            'replacements_count'.
        """
        if not isinstance(markdown, str):
            return Err(Exception("markdown must be a string"))
        if not source_domain or not target_domain:
            return Err(Exception("source_domain and target_domain must be non-empty"))

        pattern = re.compile(re.escape(source_domain))
        new_text, count = pattern.subn(target_domain, markdown)

        return Ok({
            "markdown": new_text,
            "replacements_count": count,
        })

    @staticmethod
    def extract_toc(markdown: str) -> Result:
        """Extract a table of contents from Markdown headings.

        Args:
            markdown: The markdown text.

        Returns:
            Result[list[dict], Exception]: List of dicts with 'level' (int),
            'title' (str), 'anchor' (str — slugified).
        """
        if not isinstance(markdown, str):
            return Err(Exception("markdown must be a string"))

        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        toc: list[dict] = []

        for match in heading_pattern.finditer(markdown):
            level = len(match.group(1))
            title = match.group(2).strip()
            # Slugify: lowercase, replace spaces with hyphens, remove non-alnum
            anchor = re.sub(r'[^a-z0-9\-]', '', title.lower().replace(' ', '-'))
            toc.append({"level": level, "title": title, "anchor": anchor})

        return Ok(toc)
