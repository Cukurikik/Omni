"""OmniLevenshteinDistanceEngine — Production-grade edit distance computation.

Implements Wagner-Fischer dynamic programming algorithm for Levenshtein edit distance,
with full edit operation trace (insert, delete, substitute) and similarity ratio.
"""
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniLevenshteinDistanceEngine:
    """Production engine for string edit distance via Wagner-Fischer DP."""

    ENGINE_VERSION = "1.0.0"

    def compute_distance(self, s1: str, s2: str) -> Result:
        """
        Compute Levenshtein edit distance between two strings.

        Returns:
            Result with distance, similarity ratio, and DP matrix dimensions.
        """
        try:
            m, n = len(s1), len(s2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]

            for i in range(m + 1):
                dp[i][0] = i
            for j in range(n + 1):
                dp[0][j] = j

            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s1[i - 1] == s2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1]
                    else:
                        dp[i][j] = 1 + min(dp[i - 1][j],      # delete
                                            dp[i][j - 1],      # insert
                                            dp[i - 1][j - 1])  # substitute

            distance = dp[m][n]
            max_len = max(m, n)
            similarity = round(1.0 - distance / max_len, 6) if max_len > 0 else 1.0

            return Ok({"distance": distance, "similarity": similarity,
                        "s1_length": m, "s2_length": n, "max_possible_distance": max_len})
        except Exception as e:
            return Err(e)

    def compute_edit_operations(self, s1: str, s2: str) -> Result:
        """Compute edit distance and trace back the edit operations."""
        try:
            m, n = len(s1), len(s2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(m + 1):
                dp[i][0] = i
            for j in range(n + 1):
                dp[0][j] = j
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s1[i - 1] == s2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1]
                    else:
                        dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

            ops = []
            i, j = m, n
            while i > 0 or j > 0:
                if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
                    i -= 1
                    j -= 1
                elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
                    ops.append({"op": "substitute", "from": s1[i - 1], "to": s2[j - 1], "pos": i - 1})
                    i -= 1
                    j -= 1
                elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
                    ops.append({"op": "insert", "char": s2[j - 1], "pos": i})
                    j -= 1
                elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
                    ops.append({"op": "delete", "char": s1[i - 1], "pos": i - 1})
                    i -= 1
                else:
                    break
            ops.reverse()

            return Ok({"distance": dp[m][n], "operations": ops, "operation_count": len(ops)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniLevenshteinDistanceEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(m*n) Wagner-Fischer DP"}
