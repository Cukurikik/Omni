"""OmniRegexParserEngine — Production-grade regex pattern analysis engine.

Implements regex pattern matching, group extraction, tokenization,
and pattern validation using Python's re module — wrapped in monadic Result.
"""
import re
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniRegexParserEngine:
    """Production engine for regex-based text processing."""

    ENGINE_VERSION = "1.0.0"

    def match_all(self, pattern: str, text: str) -> Result:
        """Find all matches of pattern in text."""
        try:
            compiled = re.compile(pattern)
            matches = []
            for m in compiled.finditer(text):
                matches.append({"match": m.group(), "start": m.start(), "end": m.end(),
                                 "groups": list(m.groups()) if m.groups() else []})
            return Ok({"pattern": pattern, "matches": matches, "count": len(matches)})
        except re.error as e:
            return Err(ValueError(f"Invalid regex pattern: {e}"))
        except Exception as e:
            return Err(e)

    def tokenize(self, text: str, delimiter_pattern: str = r"\s+") -> Result:
        """Split text into tokens using a regex delimiter."""
        try:
            tokens = re.split(delimiter_pattern, text.strip())
            tokens = [t for t in tokens if t]
            return Ok({"tokens": tokens, "count": len(tokens), "delimiter": delimiter_pattern})
        except re.error as e:
            return Err(ValueError(f"Invalid delimiter pattern: {e}"))
        except Exception as e:
            return Err(e)

    def validate_pattern(self, pattern: str) -> Result:
        """Validate if a regex pattern is syntactically correct."""
        try:
            re.compile(pattern)
            return Ok({"pattern": pattern, "valid": True, "groups": re.compile(pattern).groups})
        except re.error as e:
            return Ok({"pattern": pattern, "valid": False, "error": str(e)})

    def replace(self, pattern: str, replacement: str, text: str, max_count: int = 0) -> Result:
        """Replace matches of pattern with replacement string."""
        try:
            result, count = re.subn(pattern, replacement, text, count=max_count)
            return Ok({"result": result, "replacements": count, "original_length": len(text),
                        "result_length": len(result)})
        except re.error as e:
            return Err(ValueError(f"Invalid regex: {e}"))
        except Exception as e:
            return Err(e)

    def extract_groups(self, pattern: str, text: str) -> Result:
        """Perform extract groups computation.

            Args:
                    pattern: str
                    text: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            m = re.search(pattern, text)
            if not m:
                return Ok({"matched": False, "groups": {}, "positional_groups": []})
            return Ok({"matched": True, "full_match": m.group(), "groups": m.groupdict(),
                        "positional_groups": list(m.groups()), "span": [m.start(), m.end()]})
        except re.error as e:
            return Err(ValueError(f"Invalid regex: {e}"))
        except Exception as e:
            return Err(e)

    def compute_ast_topological_depth(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform compute ast topological depth computation.

            Args:
                    nodes: List[Dict[str
                    Any]]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            total_depth = 0.0
            total_comp = 0.0
            recursive_cycles = 0

            for i, node in enumerate(nodes):
                n_type = node.get("type", "LITERAL")
                base = 1.0 if n_type == "LITERAL" else 2.0
                children = float(node.get("children", 0))
                rep = float(node.get("repetition", 1))

                depth = base + (children * 0.5)
                total_depth += depth
                
                comp = (depth ** 2) / (i + 1)
                total_comp += comp
                
                if rep > 1 or n_type == "KLEENE":
                    recursive_cycles += 1

            overall = total_depth * (total_comp + 1.0)
            
            return {
                "status": "success",
                "value": {
                    "total_depth": total_depth,
                    "complexity_index": total_comp,
                    "recursive_cycles": recursive_cycles,
                    "overall_structural_index": overall
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniRegexParserEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "capabilities": ["match", "tokenize", "replace", "extract"]}
