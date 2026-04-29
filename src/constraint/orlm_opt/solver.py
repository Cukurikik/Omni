from omni.core import Result, Ok, Err

class ORLMSolver:
    def solve(self, model_path: str) -> Result[dict, FileNotFoundError]:
        import os
        if not os.path.exists(model_path):
            return Err(FileNotFoundError("Model missing"))
        return Ok({"status": "OPTIMAL"})
