from typing import Any, Tuple

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class NeedlemanWunschAligner:
    def __init__(self, match_score: int = 1, mismatch_penalty: int = -1, gap_penalty: int = -2):
        self.match = match_score
        self.mismatch = mismatch_penalty
        self.gap = gap_penalty

    def align(self, seq1: str, seq2: str) -> OmniResult:
        """
        Performs global sequence alignment using Needleman-Wunsch.
        Returns OmniResult containing a tuple of (aligned_seq1, aligned_seq2, score)
        """
        if not seq1 or not seq2:
            return OmniResult.err("Sequences cannot be empty")
            
        try:
            n = len(seq1)
            m = len(seq2)
            
            # Score matrix
            score = [[0 for _ in range(m + 1)] for _ in range(n + 1)]
            
            # Initialize gaps
            for i in range(n + 1): score[i][0] = self.gap * i
            for j in range(m + 1): score[0][j] = self.gap * j
            
            # Fill matrix
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    match = score[i - 1][j - 1] + (self.match if seq1[i - 1] == seq2[j - 1] else self.mismatch)
                    delete = score[i - 1][j] + self.gap
                    insert = score[i][j - 1] + self.gap
                    score[i][j] = max(match, delete, insert)
                    
            # Traceback
            align1, align2 = "", ""
            i, j = n, m
            while i > 0 and j > 0:
                score_current = score[i][j]
                score_diag = score[i - 1][j - 1]
                score_up = score[i][j - 1]
                score_left = score[i - 1][j]
                
                if score_current == score_diag + (self.match if seq1[i - 1] == seq2[j - 1] else self.mismatch):
                    align1 += seq1[i - 1]
                    align2 += seq2[j - 1]
                    i -= 1
                    j -= 1
                elif score_current == score_left + self.gap:
                    align1 += seq1[i - 1]
                    align2 += "-"
                    i -= 1
                elif score_current == score_up + self.gap:
                    align1 += "-"
                    align2 += seq2[j - 1]
                    j -= 1
                    
            while i > 0:
                align1 += seq1[i - 1]
                align2 += "-"
                i -= 1
            while j > 0:
                align1 += "-"
                align2 += seq2[j - 1]
                j -= 1
                
            return OmniResult.ok((align1[::-1], align2[::-1], score[n][m]))
        except Exception as e:
            return OmniResult.err(f"Alignment failed: {str(e)}")
