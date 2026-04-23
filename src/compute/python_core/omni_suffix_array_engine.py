"""OmniSuffixArrayEngine — Production-grade suffix array construction.

Implements O(N log²N) suffix array construction with LCP array computation
for substring search and pattern matching applications.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniSuffixArrayEngine:
    """Production engine for suffix array and LCP array construction."""

    ENGINE_VERSION = "1.0.0"

    def build(self, text: str) -> Result:
        """Build suffix array using prefix-doubling O(N log²N)."""
        try:
            if not text:
                return Err(ValueError("Text must be non-empty."))
            n = len(text)
            sa = list(range(n))
            rank = [ord(c) for c in text]
            tmp = [0] * n
            k = 1
            while k < n:
                def compare(a, b):
                    if rank[a] != rank[b]:
                        return rank[a] - rank[b]
                    ra = rank[a + k] if a + k < n else -1
                    rb = rank[b + k] if b + k < n else -1
                    return ra - rb
                import functools
                sa.sort(key=functools.cmp_to_key(compare))
                tmp[sa[0]] = 0
                for i in range(1, n):
                    tmp[sa[i]] = tmp[sa[i-1]]
                    if compare(sa[i-1], sa[i]) < 0:
                        tmp[sa[i]] += 1
                rank = tmp[:]
                if rank[sa[-1]] == n - 1:
                    break
                k *= 2

            return Ok({"suffix_array": sa, "length": n, "text": text})
        except Exception as e:
            return Err(e)

    def build_lcp(self, text: str, sa: List[int]) -> Result:
        """Build LCP array using Kasai's algorithm O(N)."""
        try:
            n = len(text)
            rank = [0] * n
            for i in range(n):
                rank[sa[i]] = i
            lcp = [0] * n
            h = 0
            for i in range(n):
                if rank[i] > 0:
                    j = sa[rank[i] - 1]
                    while i + h < n and j + h < n and text[i + h] == text[j + h]:
                        h += 1
                    lcp[rank[i]] = h
                    if h > 0:
                        h -= 1
            return Ok({"lcp_array": lcp, "length": n})
        except Exception as e:
            return Err(e)

    def search(self, text: str, sa: List[int], pattern: str) -> Result:
        """Binary search on suffix array for pattern O(P log N)."""
        try:
            n = len(text)
            p = len(pattern)
            lo, hi = 0, n - 1
            first = -1
            while lo <= hi:
                mid = (lo + hi) // 2
                suffix = text[sa[mid]:sa[mid] + p]
                if suffix < pattern:
                    lo = mid + 1
                elif suffix > pattern:
                    hi = mid - 1
                else:
                    first = mid
                    hi = mid - 1
            last = -1
            lo, hi = 0, n - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                suffix = text[sa[mid]:sa[mid] + p]
                if suffix < pattern:
                    lo = mid + 1
                elif suffix > pattern:
                    hi = mid - 1
                else:
                    last = mid
                    lo = mid + 1
            if first == -1:
                return Ok({"found": False, "pattern": pattern, "positions": []})
            positions = sorted(sa[first:last + 1])
            return Ok({"found": True, "pattern": pattern, "positions": positions, "count": len(positions)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniSuffixArrayEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N log²N) construction, O(P log N) search"}
