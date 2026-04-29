import math
from typing import List, Tuple

# OMNI ADS VIDEO EDIT ENGINE
# Importance-Coherence Reward evaluation zero-mock bounding.

class AdsVideoEditError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class Ads1kSegmentAssemblage:
    def __init__(self, importance_weight: float, coherence_weight: float):
        self.importance_weight = importance_weight
        self.coherence_weight = coherence_weight

    def evaluate_video_segment(self, segment_features: List[List[float]], global_context: List[float]) -> Tuple[float, str, bool]:
        """
        Pure mathematical algorithmic constraint check for ICR (Importance-Coherence Reward).
        """
        try:
            if not segment_features or not global_context:
                raise AdsVideoEditError("EMPTY_FEATURE_SET")
            
            dim = len(global_context)
            if any(len(f) != dim for f in segment_features):
                raise AdsVideoEditError("DIMENSION_MISMATCH")

            reward = 0.0
            num_frames = len(segment_features)

            for i, frame in enumerate(segment_features):
                # Importance based on projection to global context (dot product)
                importance = sum(f * g for f, g in zip(frame, global_context))
                
                # Coherence based on temporal adjacent distance
                coherence = 0.0
                if i > 0:
                    prev_frame = segment_features[i - 1]
                    # Inverse distance scaling
                    dist_sq = sum((f - p) ** 2 for f, p in zip(frame, prev_frame))
                    coherence = 1.0 / (1.0 + math.sqrt(dist_sq))
                elif num_frames == 1:
                    coherence = 1.0 # Single frame is coherent to itself

                reward += (self.importance_weight * importance) + (self.coherence_weight * coherence)

            return reward / num_frames, "", True

        except AdsVideoEditError as e:
            return 0.0, e.message, False
        except Exception as e:
            return 0.0, f"UNHANDLED_EXCEPTION: {str(e)}", False
