from typing import Any, List
import re

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class FormulaExtractor:
    def extract_latex(self, text: str) -> OmniResult:
        if not text:
            return OmniResult(None, "Empty text provided")
            
        try:
            # Regex math extraction for Scientific LLM
            formulas = re.findall(r'\$\$(.*?)\$\$', text, re.DOTALL)
            inline = re.findall(r'\$(.*?)\$', text)
            
            return OmniResult({"block": formulas, "inline": inline})
        except Exception as e:
            return OmniResult(None, str(e))
