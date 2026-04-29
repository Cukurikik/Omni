from typing import List

class OmniMLLMLearnFusion:
    """OMNI Compute Layer: Multi-Modal Large Language Learning Fusion"""
    
    def __init__(self, modalities: int = 2):
        self.modalities = modalities

    def fuse_features(self, text_vector: List[float], image_vector: List[float]) -> List[float]:
        if len(text_vector) != len(image_vector):
            return text_vector # shape mismatch fallback
            
        # Deterministic late fusion via element-wise addition
        fused = []
        for t, i in zip(text_vector, image_vector):
            fused.append(t + (i * 0.5)) # image scaled down
            
        return fused
