import re
from typing import Dict, Any, List

class OmniResult:
    def __init__(self, ok: Any = None, err: str = None):
        self.ok = ok
        self.err = err
    
    def is_ok(self) -> bool:
        return self.err is None
        
    def unwrap(self) -> Any:
        if not self.is_ok():
            raise RuntimeError(f"Unwrap failed: {self.err}")
        return self.ok

class PromptTemplateEngine:
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        # Matches {{ variable_name }}
        self.var_pattern = re.compile(r'\{\{\s*([a-zA-Z0-9_]+)\s*\}\}')

    def extract_variables(self, template_str: str) -> OmniResult:
        try:
            matches = self.var_pattern.findall(template_str)
            return OmniResult(ok=list(set(matches)))
        except Exception as e:
            return OmniResult(err=f"Extraction failed: {str(e)}")

    def render(self, template_str: str, kwargs: Dict[str, Any]) -> OmniResult:
        try:
            if not isinstance(template_str, str):
                return OmniResult(err="Template must be a string")

            vars_result = self.extract_variables(template_str)
            if not vars_result.is_ok():
                return vars_result
                
            required_vars = vars_result.unwrap()
            
            # Structural business logic: check for missing variables
            if self.strict_mode:
                missing = [v for v in required_vars if v not in kwargs]
                if missing:
                    return OmniResult(err=f"Missing required variables: {missing}")

            rendered = template_str
            for key, value in kwargs.items():
                pattern = re.compile(r'\{\{\s*' + re.escape(key) + r'\s*\}\}')
                rendered = pattern.sub(str(value), rendered)

            return OmniResult(ok=rendered)

        except Exception as e:
            return OmniResult(err=f"Render failed: {str(e)}")

    def validate_dataset_alignment(self, template_str: str, df_columns: List[str]) -> OmniResult:
        """ Ensures a prompt template can be applied to a dataset schema. """
        vars_res = self.extract_variables(template_str)
        if not vars_res.is_ok():
            return vars_res
            
        required_vars = vars_res.unwrap()
        missing = [v for v in required_vars if v not in df_columns]
        
        if missing:
            return OmniResult(err=f"Template requires columns not in dataset: {missing}")
            
        return OmniResult(ok=True)
