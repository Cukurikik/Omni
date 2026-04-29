# Omni Language-Quantized Autoencoder
# Ref: haoliuhl/language-quantized-autoencoders
import math
from typing import List, Dict

def compute_codebook_distance(emb: List[float], codebook: List[List[float]]) -> int:
    best_idx, best_dist = 0, float('inf')
    for i, code in enumerate(codebook):
        dist = sum((a - b) ** 2 for a, b in zip(emb, code))
        if dist < best_dist: best_dist = dist; best_idx = i
    return best_idx

def quantize(embedding: List[float], codebook: List[List[float]]) -> Dict:
    idx = compute_codebook_distance(embedding, codebook)
    quantized = codebook[idx]
    commit_loss = sum((a - b) ** 2 for a, b in zip(embedding, quantized))
    return {"index": idx, "quantized": quantized, "commit_loss": round(commit_loss, 8)}

def vq_loss(z_e: List[float], z_q: List[float], beta: float = 0.25) -> float:
    sg_loss = sum((a - b) ** 2 for a, b in zip(z_e, z_q))
    commit = sum((a - b) ** 2 for a, b in zip(z_e, z_q))
    return round(sg_loss + beta * commit, 8)
