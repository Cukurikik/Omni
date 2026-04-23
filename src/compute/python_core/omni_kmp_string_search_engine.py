"""OmniKmpStringSearchEngine — Production-grade KMP string matching.

Implements Knuth-Morris-Pratt algorithm with O(N+M) time complexity
using failure function preprocessing for efficient pattern matching.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniKmpStringSearchEngine:
    """Production engine for KMP string matching."""

    ENGINE_VERSION = "1.0.0"

    def build_failure(self, pattern: str) -> Result:
        """Perform build failure computation.

            Args:
                    pattern: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            m = len(pattern)
            failure = [0] * m
            j = 0
            for i in range(1, m):
                while j > 0 and pattern[i] != pattern[j]:
                    j = failure[j - 1]
                if pattern[i] == pattern[j]:
                    j += 1
                failure[i] = j
            return Ok({"failure_function": failure, "pattern_length": m})
        except Exception as e:
            return Err(e)

    def search(self, text: str, pattern: str) -> Result:
        """Perform search computation.

            Args:
                    text: str
                    pattern: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if not pattern:
                return Err(ValueError("Pattern must be non-empty."))
            n, m = len(text), len(pattern)
            failure_r = self.build_failure(pattern)
            if not failure_r.is_ok():
                return failure_r
            failure = failure_r.value["failure_function"]
            matches = []
            j = 0
            comparisons = 0
            for i in range(n):
                comparisons += 1
                while j > 0 and text[i] != pattern[j]:
                    j = failure[j - 1]
                    comparisons += 1
                if text[i] == pattern[j]:
                    j += 1
                if j == m:
                    matches.append(i - m + 1)
                    j = failure[j - 1]
            return Ok({"matches": matches, "count": len(matches), "comparisons": comparisons,
                        "text_length": n, "pattern_length": m})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniKmpStringSearchEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N+M) KMP"}
