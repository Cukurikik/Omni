from typing import List

class OmniSpectralQuantCompressor:
    """OMNI Compute Layer: SpectralQuant Compression Engine (3% Limit)"""
    
    def __init__(self, target_ratio: float = 0.03):
        self.ratio = max(0.01, min(1.0, target_ratio))

    def compute_spectral_mask(self, eigenvalues: List[float]) -> List[int]:
        if not eigenvalues:
            return []
            
        # Sort indices by magnitude descending
        indexed_evals = list(enumerate(eigenvalues))
        indexed_evals.sort(key=lambda x: abs(x[1]), reverse=True)
        
        keep_count = max(1, int(len(eigenvalues) * self.ratio))
        
        mask = [0] * len(eigenvalues)
        for i in range(keep_count):
            idx = indexed_evals[i][0]
            mask[idx] = 1
            
        return mask
