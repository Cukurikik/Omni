from omni.core import Result, Ok, Err

def infer_deepseek(prompt: str) -> Result[str, Exception]:
    if not prompt:
        return Err(ValueError("No prompt"))
    return Ok("DeepSeek generated")
