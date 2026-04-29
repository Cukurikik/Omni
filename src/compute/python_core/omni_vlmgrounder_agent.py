from typing import Dict, List

class OmniVLMGrounderAgent:
    """OMNI Compute Layer: VLMGrounder 3D Visual Agent (Zero-Mock)"""
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.threshold = confidence_threshold

    def filter_bboxes(self, bboxes: List[Dict[str, float]]) -> List[Dict[str, float]]:
        filtered = []
        for bbox in bboxes:
            conf = bbox.get("confidence", 0.0)
            if conf >= self.threshold:
                filtered.append(bbox)
        return filtered
