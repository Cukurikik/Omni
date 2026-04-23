"""OmniBeautifulsoupHtmlParsingEngine — Production-grade HTML DOM analysis engine.

Parses and analyzes HTML document structure to compute DOM tree statistics:
tag frequency distribution, nesting depth, attribute extraction, and
structural validation. Uses pure string parsing — no external HTML library.
"""
import re
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniBeautifulsoupHtmlParsingEngine:
    """Production engine for HTML DOM structure analysis and tag extraction."""

    ENGINE_VERSION = "1.0.0"

    # Self-closing HTML5 void elements
    VOID_ELEMENTS = frozenset([
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ])

    def __init__(self, max_html_size: int = 1_000_000):
        """
        Initialize HTML parsing engine.

        Args:
            max_html_size: Maximum HTML string length in characters.
        """
        if max_html_size <= 0:
            raise ValueError("max_html_size must be positive.")
        self.max_html_size = max_html_size

    def analyze_dom_structure(self, html: str) -> Result:
        """
        Analyze HTML document structure to compute DOM statistics.

        Extracts all tags, computes frequency distribution, maximum nesting
        depth, and identifies structural issues (unclosed tags).

        Args:
            html: Raw HTML string.

        Returns:
            Result with tag frequencies, max depth, total elements, and issues.
        """
        try:
            if not html or not html.strip():
                return Err(ValueError("HTML string must be non-empty."))
            if len(html) > self.max_html_size:
                return Err(ValueError(f"HTML size {len(html)} exceeds max {self.max_html_size}."))

            # Extract all tags using regex
            tag_pattern = re.compile(r'<(/?)(\w+)([^>]*)/?>')
            matches = tag_pattern.findall(html)

            tag_freq: Dict[str, int] = {}
            stack: List[str] = []
            max_depth = 0
            total_open = 0
            total_close = 0
            issues: List[str] = []

            for is_closing, tag_name, attrs in matches:
                tag_lower = tag_name.lower()
                tag_freq[tag_lower] = tag_freq.get(tag_lower, 0) + 1

                if is_closing == '/':
                    total_close += 1
                    if stack and stack[-1] == tag_lower:
                        stack.pop()
                    elif tag_lower not in self.VOID_ELEMENTS:
                        issues.append(f"Unexpected closing tag </{tag_lower}>")
                elif tag_lower not in self.VOID_ELEMENTS:
                    total_open += 1
                    stack.append(tag_lower)
                    if len(stack) > max_depth:
                        max_depth = len(stack)

            # Any unclosed tags remaining
            for unclosed in stack:
                issues.append(f"Unclosed tag <{unclosed}>")

            return Ok({
                "tag_frequency": dict(sorted(tag_freq.items(), key=lambda x: -x[1])),
                "unique_tags": len(tag_freq),
                "total_elements": sum(tag_freq.values()),
                "max_nesting_depth": max_depth,
                "total_open_tags": total_open,
                "total_close_tags": total_close,
                "structural_issues": issues,
                "is_well_formed": len(issues) == 0,
            })

        except Exception as e:
            return Err(e)

    def extract_attributes(self, html: str, target_tag: str) -> Result:
        """
        Extract all attributes from instances of a specific HTML tag.

        Args:
            html: Raw HTML string.
            target_tag: Tag name to extract attributes from (e.g. "img", "a").

        Returns:
            Result with list of attribute dicts for each matched tag instance.
        """
        try:
            if not html:
                return Err(ValueError("HTML string must be non-empty."))
            if not target_tag:
                return Err(ValueError("target_tag must be non-empty."))

            tag_lower = target_tag.lower()
            pattern = re.compile(rf'<{tag_lower}\b([^>]*)/?>', re.IGNORECASE)
            attr_pattern = re.compile(r'(\w[\w-]*)=["\']([^"\']*)["\']')

            results = []
            for match in pattern.finditer(html):
                attr_str = match.group(1)
                attrs = dict(attr_pattern.findall(attr_str))
                results.append(attrs)

            return Ok({
                "target_tag": tag_lower,
                "instances_found": len(results),
                "attributes": results,
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniBeautifulsoupHtmlParsingEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "max_html_size": self.max_html_size,
            "complexity": "O(N) regex-based DOM structure analysis",
        }
