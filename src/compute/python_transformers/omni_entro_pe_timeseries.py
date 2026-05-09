"""OMNI Compute — EntroPE Time Series Forecasting"""
import logging
import math
from typing import List, Dict

logger = logging.getLogger("omni.entro_pe")

class EntropyGuidedPatchEncoder:
    """
    EntroPE: Entropy-Guided Dynamic Patch Encoder for Time Series Forecasting.
    Varies patch sizes dynamically based on the information entropy of the time series window.
    """
    def __init__(self, base_patch_size: int = 16, hidden_dim: int = 128):
        self.base_patch_size = base_patch_size
        self.hidden_dim = hidden_dim
        logger.info("Initialized EntroPE Dynamic Patch Encoder")

    def _calculate_entropy(self, window: List[float]) -> float:
        """Calculate Shannon entropy of the normalized time series window."""
        if not window: return 0.0
        
        # Normalize to probability distribution (pseudo-histogram)
        min_v = min(window)
        max_v = max(window)
        if max_v == min_v: return 0.0
        
        bins = [0] * 10
        for val in window:
            idx = int(((val - min_v) / (max_v - min_v)) * 9.99)
            bins[idx] += 1
            
        entropy = 0.0
        total = len(window)
        for b in bins:
            if b > 0:
                p = b / total
                entropy -= p * math.log2(p)
        return entropy

    def dynamic_patching(self, time_series: List[float]) -> List[List[float]]:
        """
        High entropy -> smaller patches (capture high frequency).
        Low entropy -> larger patches (capture low frequency trends).
        """
        patches = []
        i = 0
        n = len(time_series)
        
        while i < n:
            # Look ahead to calculate entropy
            lookahead = min(i + self.base_patch_size * 2, n)
            window = time_series[i:lookahead]
            ent = self._calculate_entropy(window)
            
            # Determine dynamic patch size
            if ent > 2.5:
                p_size = self.base_patch_size // 2 # High info, small patch
            elif ent < 1.0:
                p_size = self.base_patch_size * 2  # Low info, large patch
            else:
                p_size = self.base_patch_size      # Normal patch
                
            end_idx = min(i + p_size, n)
            patch = time_series[i:end_idx]
            
            # Pad if at the end
            if len(patch) < p_size:
                patch.extend([patch[-1]] * (p_size - len(patch)))
                
            patches.append(patch)
            i += p_size
            
        return patches

    def encode(self, patches: List[List[float]]) -> List[List[float]]:
        """Simulates linear projection of patches into hidden dimension."""
        encoded = []
        for p in patches:
            # Simulated linear layer
            emb = [sum(p) * 0.01 + j for j in range(self.hidden_dim)]
            encoded.append(emb)
        return encoded
