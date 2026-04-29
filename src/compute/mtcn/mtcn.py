import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class MTCNComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[MTCNComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class MTCNEngine:
    """
    OMNI Engine: MTCN
    Multi-Task Cascaded Network temporal clustering and temporal alignment matrices.
    """
    def __init__(self, spatial_variance: float = 0.05):
        self.spatial_variance = spatial_variance

    def compute_temporal_alignment(self, frame_features: np.ndarray) -> Result:
        try:
            if not isinstance(frame_features, np.ndarray):
                return Result(None, MTCNComputeError("Features must be np.ndarray"))
            
            if len(frame_features.shape) != 3:
                return Result(None, MTCNComputeError("Expected 3D tensor (Frames x Nodes x Feat)"))
                
            # Compute cross-covariance between consecutive frames
            frames = frame_features.shape[0]
            alignment_score = 0.0
            for i in range(frames - 1):
                f1_mean = np.mean(frame_features[i], axis=0)
                f2_mean = np.mean(frame_features[i+1], axis=0)
                cov = np.cov(f1_mean, f2_mean)[0,1]
                var_prod = np.var(f1_mean) * np.var(f2_mean)
                if var_prod > 0:
                    corr = cov / math.sqrt(var_prod)
                    alignment_score += corr
                    
            normalized_alignment = alignment_score / max(1, frames - 1)
            
            return Result({'alignment_score': normalized_alignment, 'frames_processed': frames})
        except Exception as e:
            return Result(None, MTCNComputeError(f"Alignment computation failed: {str(e)}"))

    def detect_spatial_anomalies(self, bounding_boxes: np.ndarray) -> Result:
        try:
            if bounding_boxes.shape[1] != 4:
                return Result(None, MTCNComputeError("Boxes must be [N, 4] format [x1, y1, x2, y2]"))
                
            areas = (bounding_boxes[:, 2] - bounding_boxes[:, 0]) * (bounding_boxes[:, 3] - bounding_boxes[:, 1])
            if np.any(areas <= 0):
                return Result(None, MTCNComputeError("Degenerate bounding boxes detected (Negative or Zero Area)"))
                
            mean_area = np.mean(areas)
            std_area = np.std(areas)
            
            anomalies = np.sum(np.abs(areas - mean_area) > (2.0 * std_area + self.spatial_variance))
            
            return Result({'anomaly_count': int(anomalies), 'mean_area': float(mean_area)})
        except Exception as e:
            return Result(None, MTCNComputeError(f"Anomaly detection failed: {str(e)}"))
