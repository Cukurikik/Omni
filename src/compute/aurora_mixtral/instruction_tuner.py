from omni.core import Result, Ok, Err

class InstructionTuner:
    def tune(self, dataset_path: str) -> Result[bool, FileNotFoundError]:
        import os
        if not os.path.exists(dataset_path):
            return Err(FileNotFoundError(f"Dataset missing: {dataset_path}"))
        return Ok(True)
