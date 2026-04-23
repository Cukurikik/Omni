"""OmniLongestCommonSubsequenceEngine — Production-grade LCS with DP.

Implements O(m*n) DP for LCS with full sequence reconstruction,
diff generation, and similarity scoring.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniLongestCommonSubsequenceEngine:
    """Production engine for Longest Common Subsequence computation."""

    ENGINE_VERSION = "1.0.0"

    def compute(self, a: str, b: str) -> Result:
        """Perform compute computation.

            Args:
                    a: str
                    b: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            m, n = len(a), len(b)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if a[i-1] == b[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])

            # Reconstruct LCS
            lcs = []
            i, j = m, n
            while i > 0 and j > 0:
                if a[i-1] == b[j-1]:
                    lcs.append(a[i-1])
                    i -= 1; j -= 1
                elif dp[i-1][j] > dp[i][j-1]:
                    i -= 1
                else:
                    j -= 1
            lcs.reverse()
            lcs_str = ''.join(lcs)

            similarity = (2 * len(lcs)) / (m + n) if (m + n) > 0 else 1.0

            return Ok({"lcs": lcs_str, "length": len(lcs), "similarity": round(similarity, 10),
                        "source_len": m, "target_len": n})
        except Exception as e:
            return Err(e)

    def diff(self, a: str, b: str) -> Result:
        """Generate diff operations based on LCS."""
        try:
            m, n = len(a), len(b)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if a[i-1] == b[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])

            ops = []
            i, j = m, n
            while i > 0 or j > 0:
                if i > 0 and j > 0 and a[i-1] == b[j-1]:
                    ops.append({"op": "equal", "char": a[i-1]})
                    i -= 1; j -= 1
                elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
                    ops.append({"op": "insert", "char": b[j-1]})
                    j -= 1
                else:
                    ops.append({"op": "delete", "char": a[i-1]})
                    i -= 1
            ops.reverse()
            return Ok({"diff": ops, "lcs_length": dp[m][n]})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniLongestCommonSubsequenceEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(m*n) DP with reconstruction"}
