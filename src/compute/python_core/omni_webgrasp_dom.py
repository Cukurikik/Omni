from typing import List, Dict

class OmniWebGraspDOM:
    """OMNI Compute Layer: WebGrasp DOM Grounding (Zero-Mock)"""
    
    def __init__(self, viewport_width: int, viewport_height: int):
        self.vw = viewport_width
        self.vh = viewport_height

    def extract_clickable_elements(self, dom_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        clickables = []
        for node in dom_nodes:
            if node.get('tag') in ['button', 'a', 'input']:
                bounds = node.get('bounds', [0,0,0,0])
                # Check visibility inside viewport
                if 0 <= bounds[0] < self.vw and 0 <= bounds[1] < self.vh:
                    clickables.append(node)
        return clickables
