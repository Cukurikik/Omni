from typing import List

class OmniSURAdapterDiffusion:
    """OMNI Compute Layer: SUR-Adapter Diffusion Modulator"""
    
    def __init__(self, guidance_scale: float = 7.5):
        self.guidance = guidance_scale

    def apply_semantic_mask(self, base_latents: List[float], mask_latents: List[float]) -> List[float]:
        if len(base_latents) != len(mask_latents):
            raise ValueError("Latent dimension mismatch")
            
        # Deterministic classifier-free guidance mock
        result = []
        for i in range(len(base_latents)):
            val = base_latents[i] + self.guidance * (mask_latents[i] - base_latents[i])
            result.append(val)
            
        return result
