# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Grad-CAM Activation Engine (OMNI Zero-Mock Implementation)
# Implements global average pooling and ReLU weighting natively.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[List[List[float]]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[List[float]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class GradCamEngine:
    def generate_heatmap(self, activations: List[List[List[float]]], gradients: List[List[List[float]]]) -> Result:
        """
        Activations and Gradients shape: [Channels][Height][Width]
        """
        if not activations or not gradients:
             return Result.err("Activations/Gradients empty.")
             
        channels = len(activations)
        if channels != len(gradients):
             return Result.err("Channel dimension mismatch betwen activations and gradients.")
             
        height = len(activations[0])
        width = len(activations[0][0])
        
        # Calculate Alpha (Global Average Pooling on gradients)
        alphas = [0.0] * channels
        for c in range(channels):
            grad_sum = 0.0
            for h in range(height):
                for w in range(width):
                    grad_sum += gradients[c][h][w]
            alphas[c] = grad_sum / (height * width)
            
        # Weighted combination mapping
        heatmap = [[0.0] * width for _ in range(height)]
        for h in range(height):
             for w in range(width):
                 pixel_val = 0.0
                 for c in range(channels):
                      pixel_val += alphas[c] * activations[c][h][w]
                 # ReLU application
                 heatmap[h][w] = max(0.0, pixel_val)
                 
        # Normalization [0, 1]
        max_val = max(max(row) for row in heatmap)
        if max_val > 0:
             for h in range(height):
                 for w in range(width):
                     heatmap[h][w] /= max_val
                     
        return Result.ok(heatmap)
