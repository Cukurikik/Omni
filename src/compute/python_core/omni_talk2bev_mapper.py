from typing import Dict, Tuple

class OmniTalk2BEVMapper:
    """OMNI Compute Layer: Talk2BEV Bird's Eye View Spatial Mapper"""
    
    def __init__(self, grid_size: int = 256):
        self.grid = grid_size

    def coordinate_to_grid(self, x: float, y: float, resolution: float) -> Tuple[int, int]:
        # Convert continuous metric coordinates to discrete grid indices
        grid_x = int((x / resolution) + (self.grid / 2))
        grid_y = int((y / resolution) + (self.grid / 2))
        
        # Bound
        grid_x = max(0, min(self.grid - 1, grid_x))
        grid_y = max(0, min(self.grid - 1, grid_y))
        
        return (grid_x, grid_y)

    def describe_scene(self, object_counts: Dict[str, int]) -> str:
        if not object_counts:
            return "The scene is empty."
            
        desc = "In this bird's eye view, I see: "
        items = [f"{v} {k}(s)" for k, v in object_counts.items()]
        return desc + ", ".join(items) + "."
