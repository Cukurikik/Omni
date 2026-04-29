from omni.core import Result, Ok, Err

class DSEvaluator:
    def evaluate_code(self, source_code: str) -> Result[float, SyntaxError]:
        if "TODO" in source_code:
            return Err(SyntaxError("Code contains uncompleted TODOs"))
        return Ok(95.5)
