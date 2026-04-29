"""
OMNI Compute Layer: Image Augmentor Matrix Operations
Transforms tensors purely through numpy/matrix multiplication.
"""
import numpy as np
from typing import Tuple, Optional

Result = Tuple[Optional[np.ndarray], Optional[Exception]]

class AugmentorPipeline:
    def __init__(self):
        self.operations = []

    def add_rotation(self, max_angle_deg: float):
        def rotate(img: np.ndarray) -> np.ndarray:
            angle = np.random.uniform(-max_angle_deg, max_angle_deg)
            theta = np.radians(angle)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array(((c, -s), (s, c)))
            
            # Vectorized rotation for H,W,C arrays using meshgrid
            h, w = img.shape[:2]
            cx, cy = w // 2, h // 2
            
            Y, X = np.ogrid[:h, :w]
            Y = Y - cy
            X = X - cx
            
            new_X = R[0, 0] * X + R[0, 1] * Y
            new_Y = R[1, 0] * X + R[1, 1] * Y
            
            new_X = np.clip(new_X + cx, 0, w - 1).astype(int)
            new_Y = np.clip(new_Y + cy, 0, h - 1).astype(int)
            
            return img[new_Y, new_X]
        self.operations.append(rotate)

    def add_flip_horizontal(self, probability: float = 0.5):
        def flip(img: np.ndarray) -> np.ndarray:
            if np.random.rand() < probability:
                return img[:, ::-1, ...]
            return img
        self.operations.append(flip)

    def process(self, batch: np.ndarray) -> Result:
        try:
            if len(batch.shape) not in (3, 4):
                return None, ValueError("Batch must be (B,H,W,C) or (H,W,C)")
                
            is_single = len(batch.shape) == 3
            if is_single:
                batch = batch[np.newaxis, ...]
                
            out_batch = np.zeros_like(batch)
            for i in range(batch.shape[0]):
                img = batch[i]
                for op in self.operations:
                    img = op(img)
                out_batch[i] = img
                
            return out_batch[0] if is_single else out_batch, None
        except Exception as e:
            return None, e
