from typing import List

class OmniVideoBenchEval:
    """OMNI Compute Layer: Video-Bench Evaluator (Zero-Mock)"""
    
    def __init__(self, fps: float):
        self.fps = fps

    def align_temporal_frames(self, timestamps: List[float]) -> List[int]:
        if not timestamps:
            return []
            
        # Convert timestamps to deterministic frame indices
        frames = []
        for ts in timestamps:
            frame_idx = int(ts * self.fps)
            frames.append(max(0, frame_idx))
            
        return frames
