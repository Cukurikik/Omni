from typing import Dict, Any, List

class OmniOdinSlidesGenerator:
    """OMNI Compute Layer: Odin Slides Content Generator (Zero-Mock)"""
    def __init__(self, template_config: Dict[str, Any]):
        self.template_config = template_config

    def generate_slide_content(self, raw_text: str, max_slides: int) -> List[Dict[str, str]]:
        if not raw_text:
            raise ValueError("Raw text cannot be empty.")
        
        words = raw_text.split()
        words_per_slide = len(words) // max_slides if max_slides > 0 else len(words)
        
        slides = []
        for i in range(max_slides):
            start_idx = i * words_per_slide
            end_idx = start_idx + words_per_slide if i < max_slides - 1 else len(words)
            slide_content = " ".join(words[start_idx:end_idx])
            slides.append({
                "slide_id": f"slide_{i+1}",
                "title": f"Section {i+1}",
                "content": slide_content
            })
            
        return slides
