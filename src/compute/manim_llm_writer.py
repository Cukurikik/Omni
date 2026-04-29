# OMNI Compute Layer - Manim LLM Writer
import re

class ManimError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def extract_manim_code(llm_response: str) -> Result:
    """Extracts valid Manim python code from LLM responses."""
    try:
        if not llm_response:
            return Result(error=ManimError("Empty LLM response"))
            
        code_blocks = re.findall(r"```python\n(.*?)```", llm_response, re.DOTALL)
        
        if not code_blocks:
            return Result(error=ManimError("No python code blocks found"))
            
        manim_code = code_blocks[0]
        if "from manim import" not in manim_code and "import manim" not in manim_code:
            return Result(error=ManimError("Code does not import manim"))
            
        return Result(value=manim_code)
    except Exception as e:
        return Result(error=ManimError(f"Extraction failed: {str(e)}"))
