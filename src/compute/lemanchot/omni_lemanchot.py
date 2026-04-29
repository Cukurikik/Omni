from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import numpy as np

# OMNI Lemanchot Engine
# Computational Layer
# Zero-mock bounding box extractor for thermal and visual anomaly detection

@dataclass
class AnomalyResult:
    ok: bool
    bounding_boxes: List[Tuple[int, int, int, int, float]] = None
    error: str = None

class OmniLemanchotAnalysis:
    def __init__(self, threshold_heat: float = 0.85):
        self.threshold = threshold_heat
        self.scans_performed = 0

    def analyze_thermal_matrix(self, thermal_data: np.ndarray, base_temperature: float = 25.0) -> AnomalyResult:
        """
        Mathematically processes a 2D grid matrix of thermal readings to identify and bound
        contiguous areas exceeding safety thresholds. NO mock arrays.
        """
        if not isinstance(thermal_data, np.ndarray) or thermal_data.ndim != 2:
            return AnomalyResult(False, error="LemanchotError: Input must be a 2D numpy array representing a thermal grid.")
        
        self.scans_performed += 1
        height, width = thermal_data.shape
        
        # Calculate dynamic threshold based on base temp
        # Anything above base + (100 * self.threshold) is an anomaly
        critical_temp = base_temperature + (100.0 * self.threshold)
        
        # Boolean mask of anomalies
        anomaly_mask = thermal_data > critical_temp
        
        if not np.any(anomaly_mask):
            return AnomalyResult(True, bounding_boxes=[])

        # Mathematical morphological box extraction (Connected Components emulation logic)
        # We iterate over rows and cols and merge boxes.
        boxes = []
        visited = np.zeros_like(anomaly_mask, dtype=bool)
        
        for y in range(height):
            for x in range(width):
                if anomaly_mask[y, x] and not visited[y, x]:
                    # Start Flood-fill to find bounding box mathematically
                    stack = [(x, y)]
                    min_x, min_y, max_x, max_y = x, y, x, y
                    max_temp = thermal_data[y, x]
                    
                    while stack:
                        cx, cy = stack.pop()
                        if cx < 0 or cx >= width or cy < 0 or cy >= height:
                            continue
                        if visited[cy, cx] or not anomaly_mask[cy, cx]:
                            continue
                            
                        visited[cy, cx] = True
                        
                        max_temp = max(max_temp, thermal_data[cy, cx])
                        min_x = min(min_x, cx)
                        min_y = min(min_y, cy)
                        max_x = max(max_x, cx)
                        max_y = max(max_y, cy)
                        
                        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
                    
                    # Store bounding box (x_min, y_min, x_max, y_max, confidence/max_val)
                    boxes.append((int(min_x), int(min_y), int(max_x), int(max_y), float(max_temp)))

        return AnomalyResult(True, bounding_boxes=boxes)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniLemanchotAnalysis",
            "threshold": self.threshold,
            "scans": self.scans_performed,
            "status": "Operational"
        }
