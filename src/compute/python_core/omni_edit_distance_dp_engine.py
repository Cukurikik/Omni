"""OmniEditDistanceDpEngine — Production-grade edit distance with operations trace.

Extends Wagner-Fischer with full operation reconstruction (insert, delete, substitute),
weighted edits, and Damerau-Levenshtein (transposition) support.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniEditDistanceDpEngine:
    """Production engine for weighted edit distance with operation trace."""

    ENGINE_VERSION = "1.0.0"

    def compute(self, s: str, t: str, insert_cost: float = 1.0,
                delete_cost: float = 1.0, sub_cost: float = 1.0) -> Result:
        """Perform edit distance computation.

        Args:
            s: Source string.
            t: Target string.
            insert_cost: Cost of insertion operation.
            delete_cost: Cost of deletion operation.
            sub_cost: Cost of substitution operation.

        Returns:
            Result: Monadic result wrapping the computed distance and operations.
        """
        try:
            m, n = len(s), len(t)
            dp = [[0.0] * (n + 1) for _ in range(m + 1)]
            for i in range(m + 1):
                dp[i][0] = i * delete_cost
            for j in range(n + 1):
                dp[0][j] = j * insert_cost
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s[i-1] == t[j-1]:
                        dp[i][j] = dp[i-1][j-1]
                    else:
                        dp[i][j] = min(dp[i-1][j] + delete_cost,
                                       dp[i][j-1] + insert_cost,
                                       dp[i-1][j-1] + sub_cost)
            # Trace operations
            ops = []
            i, j = m, n
            while i > 0 or j > 0:
                if i > 0 and j > 0 and s[i-1] == t[j-1]:
                    ops.append({"op": "match", "from": s[i-1], "to": t[j-1], "pos_s": i-1, "pos_t": j-1})
                    i -= 1; j -= 1
                elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + sub_cost:
                    ops.append({"op": "substitute", "from": s[i-1], "to": t[j-1], "pos_s": i-1, "pos_t": j-1})
                    i -= 1; j -= 1
                elif j > 0 and dp[i][j] == dp[i][j-1] + insert_cost:
                    ops.append({"op": "insert", "char": t[j-1], "pos_t": j-1})
                    j -= 1
                elif i > 0:
                    ops.append({"op": "delete", "char": s[i-1], "pos_s": i-1})
                    i -= 1
            ops.reverse()
            return Ok({"distance": dp[m][n], "operations": ops, "op_count": len([o for o in ops if o["op"] != "match"]),
                        "source_len": m, "target_len": n})
        except Exception as e:
            return Err(e)

    def damerau(self, s: str, t: str) -> Result:
        """Damerau-Levenshtein with transpositions."""
        try:
            m, n = len(s), len(t)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(m + 1):
                dp[i][0] = i
            for j in range(n + 1):
                dp[0][j] = j
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    cost = 0 if s[i-1] == t[j-1] else 1
                    dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)
                    if i > 1 and j > 1 and s[i-1] == t[j-2] and s[i-2] == t[j-1]:
                        dp[i][j] = min(dp[i][j], dp[i-2][j-2] + cost)
            return Ok({"distance": dp[m][n], "algorithm": "Damerau-Levenshtein", "source_len": m, "target_len": n})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniEditDistanceDpEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "algorithms": ["Wagner-Fischer", "Damerau-Levenshtein"]}
