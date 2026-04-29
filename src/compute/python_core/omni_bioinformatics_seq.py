# Omni BioInformatics Sequencing Engine
from typing import List, Dict

def calculate_gc_content(dna_sequence: str) -> float:
    """Calculate the GC-content of a DNA sequence."""
    if not dna_sequence:
        return 0.0
    seq = dna_sequence.upper()
    gc_count = seq.count('G') + seq.count('C')
    return round(gc_count / len(seq), 4)

def align_sequences_needleman_wunsch_score(seq1: str, seq2: str, match: int=1, mismatch: int=-1, gap: int=-1) -> int:
    """Simplified Needleman-Wunsch global alignment score."""
    n, m = len(seq1), len(seq2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(n + 1): dp[i][0] = i * gap
    for j in range(m + 1): dp[0][j] = j * gap
        
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            score = match if seq1[i-1] == seq2[j-1] else mismatch
            dp[i][j] = max(
                dp[i-1][j-1] + score,
                dp[i-1][j] + gap,
                dp[i][j-1] + gap
            )
    return dp[n][m]

def evaluate_dna_llm_generation(pred_seq: str, ref_seq: str) -> Dict[str, float]:
    score = align_sequences_needleman_wunsch_score(pred_seq, ref_seq)
    max_score = max(len(pred_seq), len(ref_seq))
    normalized = max(0.0, (score + max_score) / (2 * max_score)) if max_score > 0 else 0.0
    return {
        "alignment_score": float(score),
        "normalized_similarity": round(normalized, 4),
        "gc_delta": round(abs(calculate_gc_content(pred_seq) - calculate_gc_content(ref_seq)), 4)
    }
